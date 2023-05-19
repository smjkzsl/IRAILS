from enum import Enum
import time,os,inspect,datetime
from typing import Any, Callable,Dict, List, Optional, Sequence, Type, Union
from fastapi.routing import APIRoute 
from fastapi import (APIRouter, FastAPI, 
                     Request,
                     Response, routing,
                     status as StateCodes)
from fastapi.datastructures import Default
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.params import Depends
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from fastapi.types import DecoratedCallable
from .mvc_router import create_controller,MvcRouter as api,   register_controllers_to_app 
from .controller_utils import  TEMPLATE_PATH_KEY,AUTH_KEY, VER_KEY,get_docs  
from .config import config,ROOT_PATH,_project_name
from .log import _log,set_logger
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse,JSONResponse,ORJSONResponse
from . import midware
from . import auth
from . import database
from ._loader import _load_apps
from ._utils import get_controller_name,get_snaked_name

from ._i18n import _


__is_debug=config.get('debug',False)

def singleton(cls):
    instances = {}
    def get_instance(*args,**kwargs):
        if cls not in instances:
            instances[cls] = cls(*args,**kwargs)
        return instances[cls]
    return get_instance

@singleton
class MvcApp(FastAPI):
    def __init__(self,  **kwargs):
        self.__authObj:auth.AuthenticationBackend_ = None 
        self._data_engine:database.Engine = None
        self.__user_auth_url=""
        self.__public_auth_url=""
        self.__app_views_dirs = {} 
        self.routers_map = {}
        self.__apps_dirs = []
        super().__init__(**kwargs)
    
    @property
    def app_views_dirs(self)->Dict:
        return self.__app_views_dirs
    @app_views_dirs.setter
    def app_views_dirs(self,key,value):
        self.__app_views_dirs[key]=value
    @property
    def apps_dirs(self)->List:
        return self.__apps_dirs
    
    @property
    def public_auth_url(self):
        """public user auth url"""
        return self.__public_auth_url
    @public_auth_url.setter
    def public_auth_url(self,url):
        if self.__public_auth_url:
            _log.warning(_("public_auth_url only can be setting once time,current is:%s") % self.__public_auth_url)
        self.__public_auth_url = url
        
    @property
    def user_auth_url(self):
        """internal user auth url"""
        return self.__user_auth_url
    @user_auth_url.setter
    def user_auth_url(self,url):
        if self.__user_auth_url:
            _log.warning(_("user_auth_url only can be setting once time,current is:%s") % self.__user_auth_url)
        self.__user_auth_url = url
    @property
    def modify_authorization(self):
        return self.__authObj.casbin_auth.modify_authorization
    @property
    def authObj(self)->auth.AuthenticationBackend_:
        return self.__authObj
    
    @authObj.setter
    def authObj(self,value:auth.AuthenticationBackend_):
        self.__authObj = value
     
    @property 
    def data_engine(self)->database.Engine:
        return self._data_engine
    @data_engine.setter
    def data_engine(self,value):
        self._data_engine = value
    def __repr__(self):
        return f'<IRails:{self.title}>'
    def route(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.http,MVC app not allow to use this direct!"))
        #return super().route(path, methods, name, include_in_schema)
    def post(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.post,MVC app not allow to use this direct!"))
        #return super().post(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    
    def get(self,*args,**kwargs):
        #return super().get(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
        raise RuntimeError(_("Please use api.get,MVC app not allow to use this direct!"))
    def head(self, *args,**kwargs):
        """disabled"""
        raise RuntimeError(_("Please use api.head,MVC app not allow to use this direct!"))
        #return super().head(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    def put(self, *args,**kwargs):
        """disabled"""
        raise RuntimeError(_("Please use api.put,MVC app not allow to use this direct!"))
        #return super().put(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    def delete(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.delete,MVC app not allow to use this direct!"))
        #return super().delete(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    def options(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.options,MVC app not allow to use this direct!"))
        #return super().options(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    def patch(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.patch,MVC app not allow to use this direct!"))
        #return super().patch(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    def trace(self, *args,**kwargs):
        '''disabled'''
        raise RuntimeError(_("Please use api.trace,MVC app not allow to use this direct!"))
        #return super().trace(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
    
__app = MvcApp( ) 

__all_controller__ = {}

application = __app
api.init(application)

 
def check_init_database(): 
    db_cfg = config.get("database")
    db_uri:str = db_cfg.get("uri")
    if db_uri: 
        application.data_engine=database.init_database(db_uri,__is_debug,cfg=db_cfg)
    else:
        _log.warn(_("Warning: database.uri is empty in config"))
    return db_cfg

def __init_auth(app,auth_type:str,casbin_adapter_class,__adapter_uri):
    
    
    auth_class = auth.get_auth_backend(auth_type)
    if not auth_class:
        raise RuntimeError(_("%s auth type not support") % auth_type)
    
    
    secret_key = config.get("auth").get(f"secret_key","")
    kwargs = {'secret_key':secret_key,'adapter_uri':__adapter_uri} 
    return auth.init(app=app, backend = auth_class,adapter_class=casbin_adapter_class, **kwargs)


def api_router(path:str="", version:str="",**allargs):  
    '''
    :param path :special path format ,ex. '/{controller}/{version}'
           if given any value,it's will be ensure {controller} flag in here auto
    :param version :str like 'v1.0' ,'2.0'..
           if given any value,the :path will have {controller} flag auto
    '''
    if not 'auth' in allargs:
        allargs['auth'] = 'none'

    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_code.co_filename
    relative_path = caller_file.replace(ROOT_PATH,"")
    if relative_path.count(os.sep)>2:
        app_dir = os.sep.join(relative_path.split(os.sep)[:-2]) # os.path.dirname(os.path.dirname(relative_path)).replace(os.sep,"")
    else:
        raise RuntimeError(_("app dir must in apps dir"))
     

    def format_path(p,v):
        if p and not p.startswith("/"):
            raise RuntimeError(_("route path must start with '/',%s is not alowed!") % p)
        if p and  '{controller}' not in p :
            p += '/{controller}' 
            p += '/{version}' if v else ''
        if v and not path:
            p = "/{controller}/{version}"
        return p
    path = format_path(path,version) 
     
    abs_path = os.path.join(ROOT_PATH,app_dir.lstrip(os.sep))

    if os.path.dirname(abs_path) not in application.apps_dirs:
        application.apps_dirs.append(os.path.dirname(abs_path))
    
    _controllerBase = create_controller(path,version)  
    
    
    
    
    def _wapper(targetController):  
        _name = app_dir.replace(os.sep,".").lstrip(".") + "." + targetController.__name__ + "@" + version 
        _controller_hash = f"{_name}" 
        if not _controller_hash in __all_controller__:
            __all_controller__[_controller_hash] = {'label':'new','obj': _controllerBase}

        class puppetController( targetController ,_controllerBase ): 
            '''puppet class inherited by the User defined controller class '''
            def __init__(self,**kwags) -> None: 
                
                super().__init__()
            def _user_logout(self,msg=_('you are successed logout!'),redirect:str="/"):
                """see .core.py"""
                self.flash  = msg
                if  hasattr(application,'authObj'):
                    application.authObj.clear_userinfo(request=self.request)
                accept_header = self.request.headers.get("Accept")    
                if accept_header == "application/json":
                    return {'status':'success','msg':msg}
                else:
                    return self.redirect(redirect)
            def _verity_successed(self,user, msg=_("User authentication successed!"),redirect='/'):
                '''call by targetController''' 
                 
                self.flash  = msg
                accept_header = self._request.headers.get("Accept")
                if  hasattr(application,'authObj'):
                    access_token = application.authObj.create_access_token(user,request=self.request)
                
                    if accept_header == "application/json":
                        return {'status':'success','msg':msg,'token':str(access_token)}
                     
                else:  
                    if accept_header == "application/json":
                        return {'status':'success','msg':msg }
                 
                return RedirectResponse(redirect,status_code=StateCodes.HTTP_303_SEE_OTHER)
            def _verity_error(self,msg=_("User authentication failed!")):
                '''call by targetController'''
                 
                self.flash  = msg 
                
                accept_header = self.request.headers.get("Accept")
                if accept_header == "application/json":
                    return JSONResponse(content={'status':StateCodes.HTTP_200_OK,'msg':msg})
                url =  self.request.headers.get("Referer") or '/'
                return RedirectResponse(url,status_code=StateCodes.HTTP_303_SEE_OTHER),None
            
            @classmethod
            async def _auth__(cls,request:Request,response:Response,**kwargs):
                '''called by .controller_util.py->route_method'''
                auth_type = kwargs['auth_type'] 
                
                if not hasattr(application,'authObj') or application.authObj is None:
                    return True,None
                
                kwargs['session'] = request.session  
                ret,user = await application.authObj.authenticate(request,**kwargs)
                if user==auth.AUTH_EXPIRED:
                    request.session['flash']  = _("your authencation has been expired!"  )
                    user = False
                if auth_type=='none':
                    return True,user
                def add_redirect_param(url: str, redirect_url: str) -> str:
                    if "?" in url:
                        return url + "&redirect=" + redirect_url
                    else:
                        return url + "?redirect=" + redirect_url
                accept_header = request.headers.get("Accept")
                if user: #continue singture 
                    if config.get("session").get('auto_refresh_token',True):
                        application.authObj.create_access_token(user=user, expires_delta=None,request=request)
                #
                if not ret and not user: 
                    # _log.debug(_('Failed Auth on type:%s at url:%s') % (auth_type,str(request.url)))
                    if accept_header == "application/json":
                        return  ORJSONResponse(content={"message": "401 UNAUTHORIZED!"},
                                                   status_code=StateCodes.HTTP_401_UNAUTHORIZED),None
                    _auth_url = getattr(application,f"{auth_type}_auth_url") 

                    if _auth_url: 
                        if 'flash' not in request.session:
                            request.session['flash']=''
                        if request.session['flash']=="":
                            request.session['flash']  = _("you are not authenticated,please login!")
                        _auth_url = add_redirect_param(_auth_url,str(request.url))
                        return RedirectResponse(_auth_url,status_code=StateCodes.HTTP_303_SEE_OTHER),None
                    else:  
                        return RedirectResponse('/',status_code=StateCodes.HTTP_303_SEE_OTHER),None
                elif user:
                    _log.debug(_('Failed Auth on type:%s at url:%s  [User:%s]') % (auth_type,str(request.url),str(user)))
                    return ret,user
                return  False,None
        setattr(puppetController,AUTH_KEY,allargs['auth'])         
        setattr(puppetController,"__name__",targetController.__name__)  
        
         
        
        setattr(puppetController,"__version__",version)  
        
        setattr(puppetController,"__appdir__",abs_path)  

        
        #for generate url_for function
        url_path = path
        controller_path_name = get_snaked_name(get_controller_name(targetController.__name__))
        _view_url_path:str = url_path.replace("{controller}",controller_path_name).replace("{version}",version)  
        
        controller_current_view_path = abs_path + '/views/' + controller_path_name
        if version:
            controller_current_view_path += '/' + version
        setattr(puppetController,"__view_url__",_view_url_path) 

        #add app dir sub views to StaticFiles
        if not controller_current_view_path in application.app_views_dirs: #ensure  load it once
            application.app_views_dirs[controller_current_view_path.lower()] = _view_url_path.lower() 
            #path match static files
            
            
 
        return puppetController 
    return _wapper #: @puppetController 


def get_wrapped_endpoint(func):
    ret = func
    while hasattr(ret,'__wrapped__'):
        ret = getattr(ret,'__wrapped__')
    return ret
def _register_controllers():
    global __is_debug
    all_routers = []
    all_routers_map = {}
    for hash,dict_obj in __all_controller__.items():

        if dict_obj['label'] == 'new':
            if __is_debug:  
                _log.info(hash+" mountting...")
            all_routers.append(register_controllers_to_app(application, dict_obj['obj']))
            dict_obj['label'] = 'mounted'

    for router in all_routers:
        for r in router.routes:
            funcname = str(r.endpoint).split('<function ')[1].split(" at ")[0] 
            end_point_abs = get_wrapped_endpoint(r.endpoint)
            auth_type = getattr(end_point_abs,AUTH_KEY) if hasattr(end_point_abs,AUTH_KEY) else 'None'
            doc_map =  get_docs(r.description) if hasattr(r,'description') else {}
            if hasattr(r,'methods'):
                methods = r.methods
            else:
                methods = r.name
            if __is_debug:  
                _log.info((str(methods),r.path,funcname) )
            application.routers_map[funcname] = {'path':r.path,'methods':methods,'doc':doc_map,'auth':auth_type,"endpoint":r.endpoint}
      
    _log.info(_("static files mouting..."))
    midware.init(app=application,debug=__is_debug)

def check_db_migrate():
    db_cfg = config.get("database")
    if __is_debug and db_cfg:
        _log.info(_("checking database migrations...."))
    try:
            
        alembic_ini = db_cfg.get("alembic_ini",'./configs/alembic.ini')
        uri = db_cfg.get("uri")
        if uri:
            database.check_migration(application.data_engine,uri,alembic_ini)
    except database.InitDbError as e:
        raise
    except Exception as e:
        _log.disabled = False
        _log.error(e.args)
def generate_mvc_app():
    global __is_debug
     
    application.title = _project_name
    
    
    
    
    _log.info(_("loading irails apps..."))
    loaded,unloaded=_load_apps(debug=__is_debug) 
    _log.info(_('Load Apps Completed,%s loaded,%s unloaded') %(loaded,unloaded))  
    if not len(__all_controller__)>0:
        raise RuntimeError(_("not found any controller class"))
    
    _register_controllers()

    
    if __is_debug:
        _log.info(_("checking database configure..."))
    check_init_database()

    # Initializing the authentication system
    auth_type = config.get("auth", None)
    _casbin_adapter_class = None
    _adapter_uri: str = None
    if auth_type:
        auth_type = auth_type.get("type")
        if auth_type:
            # Get the adapter type from the configuration
            __type_casbin_adapter = config.get("auth").get("casbin_adapter", "file")
            _casbin_adapter_class = auth.get_adapter_module(__type_casbin_adapter)
            _adapter_uri = config.get("auth").get("adapter_uri")
            # Raise an error if the adapter is not supported
            if not _casbin_adapter_class:
                raise RuntimeError(_("Not support %s ,Adapter config error in auth.casbin_adapter") % __type_casbin_adapter)
    # Check for database migrations
    check_db_migrate()
    # Initialize the authentication system if the adapter class and URI are present
    if _casbin_adapter_class and _adapter_uri:
        _adapter_uri = os.path.abspath(os.path.join(ROOT_PATH, _adapter_uri))
    _log.info(_("init casbin auth system..."))
    application.authObj = __init_auth(application, auth_type, _casbin_adapter_class, _adapter_uri)
    _log.info(_("load irails apps finished."))
    return application
# import subprocess
# import time
# # 定义启动和停止进程的方法
# def start_uvicon():
#     cmd = 'uvicorn main:app --host 0.0.0.0 --port 8000'
#     uvicorn_process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
#     return uvicorn_process

# def restart_uvicon(uvicorn_process):
#     uvicorn_process.terminate()
#     # 等待 10 秒后重启进程
#     time.sleep(10)
#     # 启动进程
#     uvicorn_process = start_uvicon()

    
 


# def run(app,*args,**kwargs): 
#     import uvicorn
#     global __is_debug 
#     if  "debug" in kwargs:
#         __is_debug = kwargs["debug"] 
#         del kwargs['debug'] 
#     if __is_debug:
#         kwargs['reload'] = __is_debug
#         kwargs['log_level'] = _log.level
#         kwargs['reload_dirs'] = application.apps_dirs 
#         uvicorn.run('irails.core:application', **kwargs)
   
         
        