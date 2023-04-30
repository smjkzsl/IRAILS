import time,os,inspect,datetime
from typing import Any,Dict

from fastapi import (FastAPI, 
                     Request,
                     Response,
                     status as StateCodes)
 
from .controller import create_controller,MvcRouter as api,   register_controllers_to_app 
from .controller_utils import  TEMPLATE_PATH_KEY,AUTH_KEY, VER_KEY,get_docs  
from .config import config,ROOT_PATH,_log
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse,JSONResponse,ORJSONResponse
from . import midware
from . import auth
from . import database
from ._utils import get_controller_name,get_snaked_name

__is_debug=config.get('debug',False)


class MvcApp(FastAPI):
    def __init__(self,  **kwargs):
        self._authObj:auth.AuthenticationBackend_ = None 
        self._data_engine:database.Engine = None
        self.__user_auth_url=""
        self.__public_auth_url=""
        self._app_views_dirs = {} 
        self.routers_map = {}
        super().__init__(**kwargs)
    @property
    def public_auth_url(self):
        """public user auth url"""
        return self.__public_auth_url
    @public_auth_url.setter
    def public_auth_url(self,url):
        if self.__public_auth_url:
            raise RuntimeError(f"public_auth_url only can be setting once time,current is:{self.__public_auth_url}")
        self.__public_auth_url = url
        
    @property
    def user_auth_url(self):
        """internal user auth url"""
        return self.__user_auth_url
    @user_auth_url.setter
    def user_auth_url(self,url):
        if self.__user_auth_url:
            raise RuntimeError(f"user_auth_url only can be setting once time,current is:{self.__user_auth_url}")
        self.__user_auth_url = url

    @property
    def authObj(self)->auth.AuthenticationBackend_:
        return self._authObj
    
    @authObj.setter
    def authObj(self,value:auth.AuthenticationBackend_):
        self._authObj = value
     
    @property 
    def data_engine(self)->database.Engine:
        return self._data_engine
    @data_engine.setter
    def data_engine(self,value):
        self._data_engine = value

__app = MvcApp( ) 

__all_controller__ = []

application = __app
api.init(application)



def __init_database(): 
    db_cfg = config.get("database")
    db_uri:str = db_cfg.get("uri")
    alembic_ini = db_cfg.get("alembic_ini",'./configs/alembic.ini')
    if db_uri:
        if db_uri.startswith('sqlite'):
            db_directory = os.path.dirname(db_uri.split(':///')[1])
            os.makedirs(db_directory, exist_ok=True) 
        application.data_engine=database.init_database(db_uri,__is_debug, alembic_ini,cfg=db_cfg)
    return db_cfg

def __init_auth(app,auth_type:str,casbin_adapter_class,__adapter_uri):
    
    
    auth_class = auth.get_auth_backend(auth_type)
    if not auth_class:
        raise f"{auth_type} auth type not support"
    
    
    secret_key = config.get("auth").get(f"{auth_type}_key","")
    kwargs = {'secret_key':secret_key,'adapter_uri':__adapter_uri} 
    return auth.init(app=app, backend = auth_class,adapter_class=casbin_adapter_class, **kwargs)


def api_router(path:str="", version:str="",**allargs):  
    '''
    :param path :special path format ,ex. '/{controller}/{version}'
    :param version :str like 'v1.0' ,'2.0'..
    '''
    if not 'auth' in allargs:
        allargs['auth'] = 'none'

    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_code.co_filename
    relative_path = caller_file.replace(ROOT_PATH,"")
    if relative_path.count(os.sep)>2:
        app_dir = os.sep.join(relative_path.split(os.sep)[:-2]) # os.path.dirname(os.path.dirname(relative_path)).replace(os.sep,"")
    else:
        app_dir = "app"
    app_dir = os.path.join(ROOT_PATH,app_dir.lstrip(os.sep))

    def format_path(p,v):
        if p and not p.startswith("/"):
            raise RuntimeError(f"route path must start with '/',{p} is not alowed!")
        if p and  '{controller}' not in p :
            p += '/{controller}' 
            p += '/{version}' if v else ''
        if v and not path:
            p = "/{controller}/{version}"
        return p
    path = format_path(path,version) 
     
    abs_path = app_dir
    _controllerBase = create_controller(path,version)  
        
    __all_controller__.append(_controllerBase)
    
    def _wapper(targetController):  
        
        class puppetController( targetController ,_controllerBase ): 
            '''puppet class inherited by the User defined controller class '''
            def __init__(self,**kwags) -> None: 
                
                super().__init__()
            def _user_logout(self,msg='your are successed logout!'):
                """see .core.py"""
                self.flash  = msg
                if  hasattr(application,'authObj'):
                    application.authObj.clear_userinfo(request=self.request)
                accept_header = self.request.headers.get("Accept")    
                if accept_header == "application/json":
                    return {'status':'success','msg':msg}
                else:
                    return self.redirect('/')
            def _verity_successed(self,user,redirect_url='/', msg="User authentication successed!"):
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
                 
                return RedirectResponse(redirect_url,status_code=StateCodes.HTTP_303_SEE_OTHER)
            def _verity_error(self,msg="User authentication failed!"):
                '''call by targetController'''
                 
                self.flash  = msg 
                url =  self.request.headers.get("Referer") or '/'
                accept_header = self.request.headers.get("Accept")
                if accept_header == "application/json":
                    return JSONResponse(content={'status':StateCodes.HTTP_200_OK,'msg':msg})
                return RedirectResponse(url,status_code=StateCodes.HTTP_303_SEE_OTHER),None
            
            @classmethod
            async def _auth__(cls,request:Request,response:Response,**kwargs):
                '''called by .controller_util.py->route_method'''
                auth_type = kwargs['auth_type'] 
                
                if not hasattr(application,'authObj'):
                    return True,None
                
                kwargs['session'] = request.session  
                ret,user = await application.authObj.authenticate(request,**kwargs)
                if user==auth.AUTH_EXPIRED:
                    request.session['flash']  = "your authencation has been expired!"  
                    user = False
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
                    _log.debug(f'Failed Auth[type:{auth_type}] url:'+str(request.url))
                    if accept_header == "application/json":
                        return  ORJSONResponse(content={"message": "401 UNAUTHORIZED!"},
                                                   status_code=StateCodes.HTTP_401_UNAUTHORIZED),None
                    _auth_url = getattr(application,f"{auth_type}_auth_url") 

                    if _auth_url: 
                        if 'flash' not in request.session:
                            request.session['flash']=''
                        if request.session['flash']=="":
                            request.session['flash']  = "you are not authenticated,please login!"  
                        _auth_url = add_redirect_param(_auth_url,str(request.url))
                        return RedirectResponse(_auth_url,status_code=StateCodes.HTTP_303_SEE_OTHER),None
                    else:  
                        return RedirectResponse('/',status_code=StateCodes.HTTP_303_SEE_OTHER),None
                else:
                    _log.debug(f'Successed Auth[type:{auth_type}] Url:'+str(request.url)+',User:'+str(user))
                    return ret,user

        setattr(puppetController,AUTH_KEY,allargs['auth'])         
        setattr(puppetController,"__name__",targetController.__name__)  
        controller_name = get_controller_name(targetController.__name__)
        setattr(puppetController,"__controller_name__",controller_name)  
        
        setattr(puppetController,"__version__",version)  
        setattr(puppetController,"__location__",relative_path)  
        setattr(puppetController,"__appdir__",app_dir)  

        setattr(puppetController,"__controler_url__",controller_name)  
        #for generate url_for function
        url_path = path
        # if "" == url_path:
        #     url_path = "/{controller}"
        #     if version:
        #         url_path += "/{version}"
        _view_url_path:str = url_path.replace("{controller}",controller_name).replace("{version}",version) # "/" + os.path.basename(app_dir) + '_views'  
        
        controller_current_view_path = abs_path + '/views/' + controller_name # app_dir.replace(ROOT_PATH,'').replace("\\",'/') + '/views/' + controller_name 
        if version:
            controller_current_view_path += '/' + version
        setattr(puppetController,"__view_url__",_view_url_path) 

        #add app dir sub views to StaticFiles
        if not controller_current_view_path in application._app_views_dirs: #ensure  load it once
            application._app_views_dirs[controller_current_view_path] = _view_url_path#os.path.join(app_dir,"views")
            #path match static files
            
            
 
        return puppetController 
    return _wapper #: @puppetController 


def get_wrapped_endpoint(func):
    ret = func
    while hasattr(ret,'__wrapped__'):
        ret = getattr(ret,'__wrapped__')
    return ret

def generate_mvc_app( ):
    global __is_debug
    _log.disabled = False
    from ._loader import _load_apps
   
    _log.info("\n\init mvc app...")
    loaded,unloaded=_load_apps(debug=__is_debug) 
    _log.info(f'Load Apps Completed,{loaded} loaded,{unloaded} unloaded')  
    if not len(__all_controller__)>0:
        raise RuntimeError("must use @api_route to define a controller class")
    all_routers = []
    all_routers_map = {}
    for ctrl in __all_controller__:
        all_routers.append(register_controllers_to_app(application, ctrl))
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
            all_routers_map[funcname] = {'path':r.path,'methods':methods,'doc':doc_map,'auth':auth_type}
    application.routers_map = all_routers_map  
    if __is_debug:
        _log.info("----------------------------------------------------------")
    midware.init(app=application,debug=__is_debug)
    db_cfg = __init_database()
    auth_type = config.get("auth",None)
    _casbin_adapter_class=None
    _adapter_uri:str=None
    if auth_type:
        auth_type=auth_type.get("type" )
        if auth_type:
            __type_casbin_adapter = config.get("auth").get("casbin_adapter","file")
            _casbin_adapter_class =  auth.get_adapter_module(__type_casbin_adapter)
            _adapter_uri = config.get("auth").get("adapter_uri") 
            if not _casbin_adapter_class:
                raise f"Not support {__type_casbin_adapter} ,Adapter config error in auth.casbin_adapter"
            
    
    if __is_debug and db_cfg:
        _log.info("checking database migrations....")
        try:
            #Base.metadata.create_all(engine)
            alembic_ini = db_cfg.get("alembic_ini",'./configs/alembic.ini')
            uri = db_cfg.get("uri")
            database.check_migration(application.data_engine,uri,alembic_ini)
        except Exception as e:
            _log.disabled = False
            _log.error(e.args)
    if _casbin_adapter_class and _adapter_uri:
        application.authObj = __init_auth(application,auth_type,_casbin_adapter_class,_adapter_uri)
    _log.info("init mvc app end===========================================")
    return application

def run(app,*args,**kwargs): 
    import uvicorn
    global __is_debug
    host =  "host" in kwargs  and kwargs["host"]  or '0.0.0.0' 
    port = "port" in kwargs  and kwargs["port"] or 8000  
    if  "debug" in kwargs:
        __is_debug = kwargs["debug"]  
     
    uvicorn.run(app, host=host, port=port)