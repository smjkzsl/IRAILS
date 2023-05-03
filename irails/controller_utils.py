import inspect
import re
import types
from collections import defaultdict
from functools import wraps, update_wrapper
from typing import Callable, Dict, Set, Type
import copy
import typing_inspect
from fastapi import APIRouter,Request,Response,HTTPException,Form,Depends
from .cbv import cbv
from fastapi.openapi import  utils as fastapi_dependencies_utils
from ._utils import get_snaked_name,get_controller_name

def _get_flat_params(dependant )  :
    flat_dependant =fastapi_dependencies_utils.get_flat_dependant(dependant, skip_repeats=True)
    new_params_query = []
    for _item in flat_dependant.query_params:
        if not (_item.name.startswith("__") and _item.name.endswith("__")):
            new_params_query.append(_item)
    return (
        flat_dependant.path_params
        + new_params_query
        + flat_dependant.header_params
        + flat_dependant.cookie_params
    )
# _old_get_flat_params = fastapi_dependencies_utils.get_flat_params
fastapi_dependencies_utils.get_flat_params = _get_flat_params 




TEMPLATE_PATH_KEY = "__template_path__"
VER_KEY = "__custom_version__"
PATH_KEY = "__custom_path__"
METHOD_KEY = "__custom_method__"
KWARGS_KEY = "__custom_kwargs__"
SIGNATURE_KEY = "__saved_signature__"
ARGS_KEY = "__custom_args__"
AUTH_KEY="__auth__"


class ControllerBase:
    """ """
    
    pass


CBType = Type[ControllerBase]
CBTypeSet = Set[CBType]



def _get_leaf_controllers(controller_base: CBType) -> CBTypeSet:
    """

    Args:
      controller_base: Type[ControllerBase]:

    Returns:

    """
    controllers_to_process = controller_base.__subclasses__()
    controllers = set()

    while len(controllers_to_process) > 0:
        controller_to_process = controllers_to_process.pop()

        controller_subclasses = controller_to_process.__subclasses__()

        if len(controller_subclasses) > 0:
            controllers_to_process.extend(controller_subclasses)
        else:
            controllers.add(controller_to_process)

    return controllers


def _compute_path(route_path: str, controller_name: str, path_template_prefix: str, version: str) -> str:
    """

    Args:
      route_path: str:
      controller_name: str:
      path_template_prefix: str:
      version: str:

    Returns:

    """
    controller_name = get_controller_name(controller_name)
    snake_case_controller_name = get_snaked_name(controller_name)

    return f"{path_template_prefix}{route_path}" \
        .replace("{controller}", snake_case_controller_name) \
        .replace("{version}", version)


def _get_routes_in_controller(controller: Type[ControllerBase]):
    """

    Args:
      controller: Type[ControllerBase]:

    Returns:

    """
    routes_dict = defaultdict(dict)

    controller_hierarchy = {controller}

    while len(controller_hierarchy) > 0:
        cls = controller_hierarchy.pop()

        members = filter(
            lambda x: not x[0].startswith("_") and inspect.isfunction(x[1]),
            inspect.getmembers(cls))

        for name, member in members:
            path_attr = getattr(member, PATH_KEY, None)

            if not routes_dict.get(name, {}).get(PATH_KEY, None):
                if not path_attr:
                    controller_hierarchy.add(cls.__base__)
                else:
                    routes_dict[name][PATH_KEY] = path_attr
                    routes_dict[name][METHOD_KEY] = getattr(member, METHOD_KEY, None)
                    routes_dict[name][KWARGS_KEY] = getattr(member, KWARGS_KEY, None)
                    routes_dict[name][ARGS_KEY] = getattr(member, ARGS_KEY, None)

    return routes_dict


def _get_generic_type_var_dict(controller: Type[ControllerBase]) -> Dict:
    """

    Args:
        controller:

    Returns:

    """
    generic_values = []

    generic_bases = typing_inspect.get_generic_bases(controller)

    for generic_base in generic_bases:
        generic_values.extend(typing_inspect.get_args(generic_base))

    generic_type_vars = []

    base_generic_bases = typing_inspect.get_generic_bases(controller.__base__)

    type_var_generic_bases = list(
        filter(typing_inspect.is_generic_type, base_generic_bases))

    for type_var_generic_base in type_var_generic_bases:
        generic_type_vars.extend(typing_inspect.get_args(type_var_generic_base))

    return {k: v for k, v in zip(generic_type_vars, generic_values)}


def _update_generic_parameters_signature(generic_dict: Dict, method: Callable):
    """

    Args:
        generic_dict:
        method:

    Returns:

    """
    sig = inspect.signature(method)
    params = sig.parameters

    new_params = []
    has_request:bool=False
    has_response:bool=False
    for k, v in params.items():
        annotation = v.annotation #注释
        if v.name=='request'  :
            has_request = True
        if v.name=="response"  :
            has_response = True
        if typing_inspect.is_typevar(annotation):
            new_params.append(
                inspect.Parameter(name=k, kind=v.kind, annotation=generic_dict[annotation], default=v.default))
        else:
            new_params.append(v)
     
    if not has_request: 
        new_params.append(inspect.Parameter('request', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request,default=None))
         
    if not has_response: 
        new_params.append(inspect.Parameter('response', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Response,default=None))
    new_params.append(inspect.Parameter('__has_request__', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=bool,default=has_request))
    new_params.append(inspect.Parameter('__has_response__', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=bool,default=has_response))
     
    
    return_val = generic_dict[sig.return_annotation] if typing_inspect.is_typevar(
        sig.return_annotation) else sig.return_annotation

    setattr(method, "__signature__", sig.replace(parameters=new_params, return_annotation=return_val))


def _update_generic_args(generic_dict: Dict, kwargs) -> Dict:
    """

    Args:
        generic_dict:
        kwargs:

    Returns:

    """
    for k, v in kwargs.items():
        if typing_inspect.is_generic_type(v):
            args = typing_inspect.get_args(v)
            args = [generic_dict[k] if k in generic_dict else k for k in args]
            v.__args__ = args
            kwargs[k] = v

    return kwargs


def _copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)

    Args:
        f:

    Returns:

    """

    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def _register_controller_to_router(router: APIRouter, controller: Type[ControllerBase]) -> None:
    """

    Args:
      router: APIRouter:
      controller: ControllerBase:

    Returns:

    """
    path_template = getattr(controller, TEMPLATE_PATH_KEY)
    version = getattr(controller, VER_KEY)

    # Get all the routes information
    routes_dict = _get_routes_in_controller(controller)
    generic_dict = _get_generic_type_var_dict(controller)

    for name, value in routes_dict.items():
        member = getattr(controller, name)
        new_member = _copy_func(member)
        # setattr(new_member,'__doc__',getattr(member,'__doc__'))
        _update_generic_parameters_signature(generic_dict, new_member)
        
        path = _compute_path(value[PATH_KEY], controller.__name__, path_template, version)
        kwargs = _update_generic_args(generic_dict, value[KWARGS_KEY])
         
        if isinstance(value[METHOD_KEY],list):
            route_method = getattr(router, 'api_route') 
            # 添加到 fastapi apiroute
            new_route_method = route_method(path,methods=value[METHOD_KEY], **kwargs)(new_member)
            
    
        else:
            if 'websocket' == value[METHOD_KEY]:
                route_method = getattr(router, 'websocket' )
                new_route_method = route_method(path)(new_member)
            else:
                route_method = getattr(router, value[METHOD_KEY]) 
                # 添加到 fastapi apiroute
                new_route_method = route_method(path, **kwargs)(new_member)
        setattr(controller, name, new_route_method)
    
    cbv(router)(controller)

 

 

def _route_method(path: str, method, *args, **mwargs): 
    if not path.startswith("/"):
        raise RuntimeError("path must start with '/'")
    def wrapper(func ): 
        @wraps(func)
        async def decorator(  *args, **kwargs):
            auth_type:str = getattr(func,AUTH_KEY) 
            has_request = kwargs.get("__has_request__")
            has_response = kwargs.get("__has_response__")
            module = inspect.getmodule(func)
            cls = getattr(module, func.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]) 
            #it's not instanced yet
            #instance = cls.__dict__.get('__wrapped__', None).__self__ #or cls.__dict__.get('__objclass__', None)(obj)
            response:Response = None
            result:Response = None
            
            if 'request' in kwargs and 'response' in kwargs:
                response  = kwargs["response"]
                rqst = kwargs['request']  
                #auth first then call constructor
                if auth_type:
                    auth_result,user = await cls._auth__(request=rqst,response=kwargs['response'],auth_type=auth_type)
                    if isinstance(auth_result,Response): 
                        return auth_result
                    if not auth_result:
                        raise HTTPException(status_code=403, detail="未经授权的访问" )
                        return Response(None,403)
                _constructor = getattr(cls,'_constructor_')
                await _constructor(cls,request = kwargs['request'],response=kwargs['response'])

            if 'request' in kwargs and not has_request:  
                del kwargs['request']  
            if 'response' in kwargs and not has_response:  
                del kwargs['response']  
            del kwargs["__has_request__"]
            del kwargs["__has_response__"]
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result =  func(*args,**kwargs)
            if isinstance(result,tuple):result = result[0]
            if response and isinstance(result,Response): 
                result.raw_headers.extend(response.raw_headers)
            if isinstance(result,Response):
                _deconstructor = getattr(cls,'_deconstructor_')
                ret = await _deconstructor(cls,result)
                if isinstance(ret,Response):
                    result = ret
 
            return result #end of decorator
            
        setattr(decorator, PATH_KEY, path)
        setattr(decorator, METHOD_KEY, method)
        setattr(decorator, ARGS_KEY, args)
        if '__auth_url__' in mwargs: 
            setattr(func,'__auth_url__',mwargs['__auth_url__'])
            del mwargs['__auth_url__']

        if not 'auth' in mwargs:
            mwargs["auth"] = 'none'
        setattr(func,AUTH_KEY,mwargs['auth'])
        del mwargs['auth']
        setattr(decorator, KWARGS_KEY, mwargs)
        # setattr(decorator,'__doc__',getattr(func,'__doc__'))
        setattr(decorator, "__signature__", inspect.signature(func))
        return decorator
    return wrapper

def get_docs(doc:str):
    ret = {}
    if doc:
        for line in doc.strip().split("\n"):
            if line.strip().startswith(":"):
                parts = line.lstrip(":").split(" ",maxsplit=1)
                if len(parts) == 2:
                    key, value = parts 
                    if value: 
                        ret[key] = value
    return ret