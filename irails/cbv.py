# Copied straight from https://github.com/dmontagu/fastapi-utils/blob/master/fastapi_utils/cbv.py to resolve dependency issues
import inspect
 

from typing import Any, Callable, Dict, List, Type, TypeVar, Union, get_type_hints
import uuid
from fastapi import APIRouter, Depends, Request, Response
from pydantic.typing import is_classvar
from starlette.routing import Route, WebSocketRoute
from .base_controller import _session_key,url_lang_key
from .log import get_logger
 

_log = get_logger(__name__)
T = TypeVar("T")

CBV_CLASS_KEY = "__cbv_class__"

REQUEST_VAR_NAME = "request"
RESPONSE_VAR_NAME = "response"

def cbv(router: APIRouter) -> Callable[[Type[T]], Type[T]]:
    """
    This function returns a decorator that converts the decorated into a class-based view for the provided router.
    Any methods of the decorated class that are decorated as endpoints using the router provided to this function
    will become endpoints in the router. The first positional argument to the methods (typically `self`)
    will be populated with an instance created using FastAPI's dependency-injection.
    For more detail, review the documentation at
    https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/#the-cbv-decorator
    """

    def decorator(cls: Type[T]) -> Type[T]:
        return _cbv(router, cls)

    return decorator


def _cbv(router: APIRouter, cls: Type[T]) -> Type[T]:
    """
    Replaces any methods of the provided class `cls` that are endpoints of routes in `router` with updated
    function calls that will properly inject an instance of `cls`.
    """
    _init_cbv(cls)
    cbv_router = APIRouter()
    function_members = inspect.getmembers(cls, inspect.isfunction)
    functions_set = set(func for _, func in function_members)
    cbv_routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute)) and route.endpoint in functions_set
    ]
    for route in cbv_routes:
        router.routes.remove(route)
        _update_cbv_route_endpoint_signature(cls, route)
        cbv_router.routes.append(route)
    router.include_router(cbv_router)
    return cls

async def controller_constructor(cls ,request:Request,response:Response):  
    '''don't call this'''
    
    if not _session_key in request.cookies or not request.cookies[_session_key]:
        request.cookies[_session_key] = str(uuid.uuid4()) 
    params = {}
    form_params = {}
    query_params = {}
    json_params = {}
    try:
        form_params =  await  request.form()
    except Exception as e:
        _log.info(_("when parsing `Form params` raised:")+str(e.args))
        pass

    
    try:
        json_params =  await  request.json()
    except:
        pass
    query_params = request.query_params
    cls._form = form_params
    cls._query = query_params
    cls._json = json_params
    cls._params = params
    def __init_flash(request:Request): 
        request.state.keep_flash = False 
        if 'flash' not in request.session:
            request.session['flash'] ='' 
        
    __init_flash(request=request) 

    if url_lang_key in query_params:
        lang = query_params[url_lang_key]
        request.session['lang'] = [lang]
        if hasattr(request,'user'):
            request.scope['user'].lang = lang
        
 
async def controller_destructor(cls,new_response:Response):  
    '''do not call this anywhere'''
    def process_cookies(response:Response, cookies,old_cookies):
        
        for key in cookies: 
            if   key != _session_key: 
                response.set_cookie(key,cookies[key])
        for key in old_cookies:
            if not key in cookies and key != _session_key:
                response.set_cookie(key=key,value="",max_age=0)   
        response.set_cookie(key=_session_key,
                            value=cls._request.cookies[_session_key],
                            max_age = 14 * 24 * 60 * 60,  # 14 days, in seconds
                            path  = "/",
                            samesite  = "lax",
                            httponly  = False ) 
        
    if new_response:
        process_cookies(new_response,cls._cookies,cls._request.cookies)

    def __clear_flash(request:Request):
        if not request.state.keep_flash:
            request.session['flash'] = ''
    __clear_flash(cls._request)

    
def _init_cbv(cls: Type[Any]) -> None:
    """
    Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CBV_CLASS_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]  # drop `self` parameter
    new_parameters = [
        x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: List[str] = []
    has_request=False
    has_response = False
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parameter_kwargs)
        )
        if name == REQUEST_VAR_NAME:
            has_request = True
        if name == RESPONSE_VAR_NAME:
            has_response = True

    if not has_request: 
        # dependency_names.append(REQUEST_VAR_NAME)
        new_parameters.append(inspect.Parameter(REQUEST_VAR_NAME, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request,default=None))
         
    if not has_response: 
        # dependency_names.append(RESPONSE_VAR_NAME)
        new_parameters.append(inspect.Parameter(RESPONSE_VAR_NAME, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Response,default=None))
   
    new_signature = old_signature.replace(parameters=new_parameters)

    
    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        self._request = None
        self._response = None
        if REQUEST_VAR_NAME in kwargs:
            self._request = kwargs.pop(REQUEST_VAR_NAME) 
            self._cookies:Dict[str,str] = self._request.cookies.copy()
            # base_controller_class._session = await  _sessionManager.initSession(request,response )
            self._session = self._request.session

        if RESPONSE_VAR_NAME in kwargs:
            self._response = kwargs.pop(RESPONSE_VAR_NAME)

        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
            

        old_init(self, *args, **kwargs)
        

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, CBV_CLASS_KEY, True)

    

def _update_cbv_route_endpoint_signature(cls: Type[Any], route: Union[Route, WebSocketRoute]) -> None:
    """
    Fixes the endpoint signature for a cbv route to ensure FastAPI performs dependency injection properly.
    """
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_parameters: List[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, "__signature__", new_signature)
