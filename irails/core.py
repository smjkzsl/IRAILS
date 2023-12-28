
import os
import inspect
from typing import Dict, List, Union,Callable
from urllib.parse import quote
from fastapi import (FastAPI,
                     Request,
                     Response,
                     status as StateCodes)
from fastapi.responses import RedirectResponse, JSONResponse
from .mvc_router import create_controller, Api as api,   register_controllers_to_app
from .controller_utils import AUTH_KEY, DEFAULT_KEY,  get_docs
from .config import config, ROOT_PATH, _project_name
from .log import get_logger
_log=get_logger(__name__)
from . import midware
from . import auth
from . import database
from ._loader import collect_apps
from ._utils import get_controller_name, get_snaked_name,  singleton, add_redirect_param
from ._i18n import _

__is_debug = config.get('debug', False)
auto_refresh_token = config.get("session").get('auto_refresh_token', True)


@singleton
class MvcApp(FastAPI):
    def __init__(self,  **kwargs):
        self.__casbin_auth: auth.AuthenticationBackend_ = None
        self._data_engine: database.Engine = None
        self.__user_auth_url = ""
        self.__public_auth_url = ""
        # self.__app_views_dirs = {}
        self.routers_map = {}
        self.__apps_dirs = []
        self.__apps = {}
        self.auth_user_class: auth.DomainUser = None
        self.__before_auth_func:List[Callable] = []
        
        super().__init__(**kwargs)
        # set variable in MvcRouter
        api.init(self)
    
    def before_auth(self,func):
        '''wrap a function to auth function'''
        self.__before_auth_func.append(func)

    async def _auth(self,request:Request,**kwargs)->(bool,auth.BaseUser):
        '''
         hook before auth, if one of `before_auth` is return success then never to call the lastest
        '''
        def set_flash(msg):
            if 'flash' not in request.session:
                request.session['flash'] = ''
            if request.session['flash'] == "":
                request.session['flash'] = msg
        ret = False;user:auth.BaseUser = None

        auth_type = kwargs['auth_type'].lower() 
        # if auth_type.lower() == 'none':
        #     ret = True
        if  not hasattr(application, 'casbin_auth') or \
                application.casbin_auth is None: # project not need it or not config auth item
            return True, None                
        
        kwargs['session'] = request.session 
        
        cur_func = None
        for func in self.__before_auth_func:
            cur_func = func
            user = cur_func(request,**kwargs)
            if  user:
                request.scope['user'] = user
                if auth_type=='none':
                    ret = True
                else:
                    ret = self.__casbin_auth._auth(request=request,user=user)
                break
        
        if auth_type=='none':
            ret = True
        if auth_type=='public' and user:
            ret = True

        if (not ret) and (not user or not user.is_authenticated):
            #recive and check user right or generate a anoymous user
            ret, user = await self.casbin_auth.authenticate(request, **kwargs)
        elif ret and not user:
             
            user = auth.DomainUser()
            request.scope['user'] = user
            # raise RuntimeError(_("guest user be must a anoymous user,check "+f"`before_auth` in `{_module_name}`"))
        if user == auth.AUTH_EXPIRED:
            set_flash(_(
                    "your authencation has been expired!"))
            user = auth.DomainUser()
            request.scope['user'] = user
            
        if user and user.is_authenticated:  # continue singture
            if auto_refresh_token:
                application.casbin_auth.create_access_token(
                    user=user, expires_delta=None, request=request)

        if ret:  # auth successed
            return ret, user

        #--auth failed--
        
        accept_header = request.headers.get("Accept")
        content_type = request.headers.get("Content-Type")
        is_json_mode = accept_header == 'application/json' or content_type=='application/json'
        
        _redirect_url = ""  # if this has value, will redirect if in mvc mode
        code = StateCodes.HTTP_401_UNAUTHORIZED
        code_str = '401 UNAUTHORIZED'
        if not ret and not user or not user.is_authenticated:
            # not login user redirect to login page if has redirect page(is general page)
            # if is json mode it's just return json message.
            # getattr(application, f"{auth_type}_auth_url")
            _auth_url = application.public_auth_url
            if _auth_url:
                # set flash message
                set_flash(_("you are not authenticated,please login!"))
                _redirect_url = add_redirect_param(
                    _auth_url, str(request.url))
        elif user and user.is_authenticated:
            # user is right,but it's not authenticated this resource.
            code = StateCodes.HTTP_403_FORBIDDEN
            code_str = '403 FORBIDDEN'
            msg = _('Failed Auth url:%s  [User:%s]') % (
                str(request.url), str(user))
            _log.debug(msg) 
            _auth_url = application.user_auth_url
            if _auth_url:
                set_flash(msg)
                _redirect_url = add_redirect_param(
                    _auth_url, str(request.url))

        if _redirect_url:
            if is_json_mode:
                return JSONResponse(content={"message": code_str},
                                    status_code=code), None
            else:
                return RedirectResponse(_redirect_url, status_code=StateCodes.HTTP_303_SEE_OTHER), None
        else:

            if is_json_mode:
                return JSONResponse(content={"message": code_str},
                                    status_code=code), None

            return RedirectResponse(request.headers.get("Referer") or '/',
                                    status_code=StateCodes.HTTP_303_SEE_OTHER), None
        return ret ,user
    
    def generate_auth_user(self, user: Union[database.UserBaseMixin, Dict]) -> auth.DomainUser:
        '''
        create new authencation user from givened data
        '''
        if not self.auth_user_class:
            raise RuntimeError('application.auth_class is None')
        if isinstance(user, dict):
            userobj = self.auth_user_class(username=user['name'])
            userobj.id = user.get('id','')
        elif isinstance(user, database.Base):
            userobj: auth.DomainUser = self.auth_user_class(user.username)
            # copy_attr(user, userobj, False)
            for key  in dir(user):
                value = getattr(user,key)
                if not key.startswith("__") and hasattr(userobj, key):
                    if key=='roles' and isinstance(value,list):
                        userobj.roles = [row.name for row in value]
                    else:
                        setattr(userobj, key, value)
        return userobj

    @property
    def apps(self) -> Dict:
        return self.__apps

    # @property
    # def app_views_dirs(self)->Dict:
    #     return self.__app_views_dirs
    # @app_views_dirs.setter
    # def app_views_dirs(self,key,value):
    #     self.__app_views_dirs[key]=value
    @property
    def apps_dirs(self) -> List:
        return self.__apps_dirs

    @property
    def public_auth_url(self):
        """public user auth url"""
        return self.__public_auth_url

    @public_auth_url.setter
    def public_auth_url(self, url):
        if self.__public_auth_url:
            _log.warning(
                _("public_auth_url only can be setting once time,current is:%s") % self.__public_auth_url)
        self.__public_auth_url = url

    @property
    def user_auth_url(self):
        """internal user auth url"""
        return self.__user_auth_url

    @user_auth_url.setter
    def user_auth_url(self, url):
        if self.__user_auth_url:
            _log.warning(
                _("user_auth_url only can be setting once time,current is:%s") % self.__user_auth_url)
        self.__user_auth_url = url

    @property
    def policy(self):
        return self.__casbin_auth.casbin_auth.policy

    @property
    def grouping(self):
        return self.__casbin_auth.casbin_auth.grouping

    @property
    def is_grouping(self):
        return self.__casbin_auth.casbin_auth.is_grouping

    @property
    def casbin_auth(self) -> auth.AuthenticationBackend_:
        return self.__casbin_auth

    @casbin_auth.setter
    def casbin_auth(self, value: auth.AuthenticationBackend_):
        self.__casbin_auth = value

    @property
    def data_engine(self) -> database.Engine:
        return self._data_engine

    @data_engine.setter
    def data_engine(self, value):
        self._data_engine = value

    def app_list(self, group_by_controller=False, is_installed=None) -> List:
        import copy
        apps = []
        for app_name in self.apps:
            app_is_installed = self.apps[app_name]['is_installed']
            if not is_installed is None:
                if is_installed == True:
                    if not app_is_installed:
                        continue
            manifest = copy.copy(self.apps[app_name]['manifest'])
            route_map = copy.copy(self.apps[app_name]['route_map'])
            for item in route_map:
                if 'endpoint' in route_map[item]:
                    del route_map[item]['endpoint']
            if group_by_controller:
                funcs = {}
            else:
                funcs = []
            for item in route_map:
                _item = route_map[item]
                _item.update({'function': item})
                if group_by_controller:
                    ctrl_name = item.split(".")[0]
                    funcs[ctrl_name] = _item
                    pass
                else:
                    funcs.append(_item)
            manifest.update({'is_installed': app_is_installed,
                            'app_name': app_name, 'routes': funcs})

            apps.append(manifest)
        return apps

    def __repr__(self):
        return f'<IRails:{self.title}>'

    def route(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.http,MVC app not allow to use this direct!"))
        # return super().route(path, methods, name, include_in_schema)

    def post(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.post,MVC app not allow to use this direct!"))
        # return super().post(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def get(self, *args, **kwargs):
        # return super().get(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)
        raise RuntimeError(
            _("Please use api.get,MVC app not allow to use this direct!"))

    def head(self, *args, **kwargs):
        """disabled"""
        raise RuntimeError(
            _("Please use api.head,MVC app not allow to use this direct!"))
        # return super().head(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def put(self, *args, **kwargs):
        """disabled"""
        raise RuntimeError(
            _("Please use api.put,MVC app not allow to use this direct!"))
        # return super().put(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def delete(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.delete,MVC app not allow to use this direct!"))
        # return super().delete(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def options(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.options,MVC app not allow to use this direct!"))
        # return super().options(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def patch(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.patch,MVC app not allow to use this direct!"))
        # return super().patch(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)

    def trace(self, *args, **kwargs):
        '''disabled'''
        raise RuntimeError(
            _("Please use api.trace,MVC app not allow to use this direct!"))
        # return super().trace(path, response_model=response_model, status_code=status_code, tags=tags, dependencies=dependencies, summary=summary, description=description, response_description=response_description, responses=responses, deprecated=deprecated, operation_id=operation_id, response_model_include=response_model_include, response_model_exclude=response_model_exclude, response_model_by_alias=response_model_by_alias, response_model_exclude_unset=response_model_exclude_unset, response_model_exclude_defaults=response_model_exclude_defaults, response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema, response_class=response_class, name=name, callbacks=callbacks, openapi_extra=openapi_extra, generate_unique_id_function=generate_unique_id_function)


application = MvcApp(docs_url=None, redoc_url=None)

application.root_path_in_servers = config.get("root_path_in_servers",None)
 

def check_init_database():
    db_cfg = config.get("database")
    db_uri: str = db_cfg.get("uri")
    if db_uri:
        application.data_engine = database.init_database(
            db_uri, __is_debug, cfg=db_cfg)
    else:
        _log.warn(_("Warning: database.uri is empty in config"))
    return db_cfg


def __init_auth(app, auth_type: str, casbin_adapter_class, __adapter_uri):

    auth_class = auth.get_auth_backend(auth_type)
    if not auth_class:
        raise RuntimeError(_("%s auth type not support") % auth_type)
    application.auth_user_class = auth_class.user_class

    secret_key = config.get("auth").get(f"secret_key", "")
    kwargs = {'secret_key': secret_key, 'adapter_uri': __adapter_uri}
    return auth.init(app=app, backend=auth_class, adapter_class=casbin_adapter_class, **kwargs)


def api_router(path: str = "", version: str = "", **allargs):
    '''
    :param path :special path format ,ex. '/{controller}/{version}'
           if given any value,it's will be ensure {controller} flag in here auto
           
           full path expression is ['{app}','{controller}','{version}'] 
    :param version :str like 'v1.0' ,'2.0'..
           if given any value,the :path will have {controller} flag auto
    
    :addtional params
            :auth set the auth type for member by default,may rewrite in member decorator args
            :default set default index path to a exists member
            eg. default='index' when get '/{controller}/' will execute member 'index' method
    '''
    if not 'auth' in allargs:
        allargs['auth'] = 'none'

    caller_frame = inspect.currentframe().f_back
    caller_file = caller_frame.f_code.co_filename
    relative_path = caller_file.replace(ROOT_PATH, "")
    if relative_path.count(os.sep) > 2:
        # os.path.dirname(os.path.dirname(relative_path)).replace(os.sep,"")
        app_dir = os.sep.join(relative_path.split(os.sep)[:-2])
    else:
        raise RuntimeError(_("app dir must in apps dir"))

    app_name = os.path.basename(app_dir)

    def format_path(p, v):
        if p and not p.startswith("/"):
            raise RuntimeError(
                _("route path must start with '/',%s is not alowed!") % p)
        if p and '{controller}' not in p:
            p += '/{controller}'
            p += '/{version}' if v else ''
        if v and not path:
            p = "/{controller}/{version}"

        return p.replace("{app}", app_name)
    path = format_path(path, version)

    abs_path = os.path.join(ROOT_PATH, app_dir.lstrip(os.sep))

    if os.path.dirname(abs_path) not in application.apps_dirs:
        application.apps_dirs.append(os.path.dirname(abs_path))

    _controllerBase = create_controller(path, version)

    setattr(_controllerBase, "__app_name__", app_name)

    def _wapper(targetController):
        _controller_hash = app_dir.replace(os.sep, ".").lstrip(
            ".") + "." + targetController.__name__ + "@" + version

        if not app_name in application.apps:
            application.apps[app_name] = {'routes': {}, 'view_dirs': {}}

        if not 'app_dir' in application.apps[app_name]:
            application.apps[app_name]['app_dir'] = abs_path

        if not _controller_hash in application.apps[app_name]['routes']:
            application.apps[app_name]['routes'][_controller_hash] = {
                'label': 'new', 'obj': _controllerBase}
        application.apps[app_name]['is_installed'] = True

        class puppetController(targetController, _controllerBase):
            '''puppet class inherited by the User defined controller class '''

            def __init__(self, **kwags) -> None:

                super().__init__()

            def _user_logout(self, msg=_('you are successed logout!'), redirect: str = "/"):
                """see .core.py"""
                self.flash = msg
                if hasattr(application, 'casbin_auth'):
                    application.casbin_auth.clear_userinfo(
                        request=self.request)
                accept_header = self.request.headers.get("Accept")
                if accept_header == "application/json":
                    return {'status': 'success', 'msg': msg}
                else:
                    return self.redirect(redirect)

            def _verity_successed(self, user, msg=_("User authentication successed!"), redirect='/'):
                '''call by targetController'''

                self.flash = msg
                accept_header = self._request.headers.get("Accept")
                if hasattr(application, 'casbin_auth'):
                    access_token = application.casbin_auth.create_access_token(
                        user, request=self.request)

                    if accept_header == "application/json":
                        return {'status': 'success', 'msg': msg, 'token': str(access_token)}

                else:
                    if accept_header == "application/json":
                        return {'status': 'success', 'msg': msg}

                return RedirectResponse(redirect, status_code=StateCodes.HTTP_303_SEE_OTHER)

            def _verity_error(self, msg=_("User authentication failed!")):
                '''call by targetController'''

                self.flash = msg

                accept_header = self.request.headers.get("Accept")
                if accept_header == "application/json":
                    return JSONResponse(content={'status': StateCodes.HTTP_200_OK, 'msg': msg})
                url = self.request.headers.get("Referer") or '/'
                return RedirectResponse(url, status_code=StateCodes.HTTP_303_SEE_OTHER), None

             
                # end of _auth_
        setattr(puppetController, AUTH_KEY, allargs['auth'])
        setattr(puppetController, "__name__", targetController.__name__)
        setattr(puppetController, "__version__", version)
        setattr(puppetController, "__appdir__", abs_path)
        # for generate url_for function
        
        url_path = path
        controller_path_name = get_snaked_name(
            get_controller_name(targetController.__name__))
        _view_url_path: str = url_path.replace(
            "{controller}", controller_path_name).replace("{version}", version)
        if not _view_url_path:
            _view_url_path = f"/{app_name}/{controller_path_name}"
        # _view_url_path = f"{app_name}/{_view_url_path}"
        controller_current_view_path = abs_path + '/views/' + controller_path_name
        if version:
            controller_current_view_path += '/' + version
        setattr(puppetController, "__view_url__", _view_url_path)
        if 'default' in allargs:
            default_method = allargs['default']
            setattr(targetController, DEFAULT_KEY, default_method)
            del allargs['default']
        else:
            setattr(targetController, DEFAULT_KEY, '')
        # add app dir sub views to StaticFiles
        controller_current_view_path = controller_current_view_path.lower()
        # ensure  load it once
        if not controller_current_view_path in application.apps[app_name]['view_dirs']:
            application.apps[app_name]['view_dirs'][controller_current_view_path] = _view_url_path.lower(
            )

        return puppetController
    return _wapper  # : @puppetController


def get_wrapped_endpoint(func):
    ret = func
    while hasattr(ret, '__wrapped__'):
        ret = getattr(ret, '__wrapped__')
    return ret


def _register_controllers():
    global __is_debug
    controller_count = 0
    is_startup = True
    
    for app_name in application.apps:
        for hash, dict_obj in application.apps[app_name]['routes'].items():
            controller_count += 1
            if dict_obj['label'] == 'new':
                # if __is_debug:
                #     _log.info(hash+" mountting...")
                app_router = register_controllers_to_app(
                    application, dict_obj['obj'])

                application.apps[app_name]['router'] = app_router
                dict_obj['label'] = 'mounted'

                for r in app_router.routes:
                    funcname = str(r.endpoint).split(
                        '<function ')[1].split(" at ")[0]
                    end_point_abs = get_wrapped_endpoint(r.endpoint)
                    auth_type = getattr(end_point_abs, AUTH_KEY) if hasattr(
                        end_point_abs, AUTH_KEY) else 'None'
                    doc_map = get_docs(r.description) if hasattr(
                        r, 'description') else {}
                    if hasattr(r, 'methods'):
                        methods = r.methods
                    else:
                        methods = r.name
                    # if __is_debug:
                    #     _log.info((str(methods), r.path, funcname))
                    if not 'route_map' in application.apps[app_name]:
                        application.apps[app_name]['route_map'] = {}
                    application.apps[app_name]['is_installed'] = True
                    application.apps[app_name]['route_map'][funcname] = {
                        'path': r.path, 'methods': methods, 'doc': doc_map, 'auth': auth_type, "endpoint": r.endpoint}
            elif dict_obj['label'] != 'new':
                is_startup = False

    if not (controller_count) > 0:
        # raise RuntimeError(_("not found any controller class"))
        return controller_count
    else:
        # _log.info(_("static files mouting..."))

        if is_startup:
            midware.init(app=application, debug=__is_debug)
        return controller_count

def check_db_migrate():
    db_cfg = config.get("database")
    if not db_cfg:
        return
     
    try:

        alembic_ini = db_cfg.get("alembic_ini", './configs/alembic.ini')
        uri = db_cfg.get("uri")
        if uri:
            database.check_migration(application.data_engine, str(application.data_engine.url), alembic_ini)
    except database.InitDbError as e:
        raise
    except Exception as e:
        _log.disabled = False
        _log.error(e.args)

    


def check_init_auth(db_cfg):
    # Initializing the authentication system
    auth_type = config.get("auth", None)
    _casbin_adapter_class = None
    _adapter_uri: str = None
    if auth_type:
        auth_type = auth_type.get("type")
        if auth_type:
            # Get the adapter type from the configuration
            __type_casbin_adapter = config.get(
                "auth").get("casbin_adapter", "file")
            _casbin_adapter_class = auth.get_adapter_module(
                __type_casbin_adapter)
            _adapter_uri = config.get("auth").get("adapter_uri")
            if not _adapter_uri:
                _adapter_uri = db_cfg.get('uri')
            # Raise an error if the adapter is not supported
            if not _casbin_adapter_class:
                raise RuntimeError(
                    _("Not support %s ,Adapter config error in auth.casbin_adapter") % __type_casbin_adapter)
    return auth_type, _adapter_uri, _casbin_adapter_class


def generate_mvc_app(env="general"):
    global __is_debug

    application.title = _project_name

    # _log.info(_("loading irails apps..."))
    _log.info("ENV:"+env)
    loaded, unloaded = collect_apps(debug=__is_debug, application=application)

    _log.info(_('Load Apps Completed,%s loaded,%s unloaded') %
              (loaded, unloaded))

    controller_count = _register_controllers()

    _log.info(_("checking database configure..."))
    db_cfg = check_init_database()

    auth_type, _adapter_uri, _casbin_adapter_class = check_init_auth(db_cfg)
    if __is_debug and env=='general':
        # Check for database migrations
        _log.info(_("checking database migrations...."))
        check_db_migrate()
        _log.info(_("check database migrations finished."))
    # Initialize the authentication system if the adapter class and URI are present

    
    _log.info(_("init casbin auth system..."))
    application.casbin_auth = __init_auth(
        application, auth_type, _casbin_adapter_class, _adapter_uri)
    _log.info(_("load irails apps finished."))
    return application

def run_server(ip:str="0.0.0.0",port:int = 8080,hot_reload=False):
    import uvicorn 
  
    kwargs = {}
    kwargs['reload'] = hot_reload 
    kwargs['host'] = ip
    kwargs['port'] = port
    
    if hot_reload:
        kwargs['factory'] = True
        app_cfg =   config.get('app')
        apps_dirs = app_cfg.get("appdirs") 
        kwargs['reload_dirs'] = list(map(os.path.abspath ,apps_dirs))
        # kwargs['reload_includes'] = []
        kwargs['reload_excludes'] = ['*.pyc','*.po']  
        uvicorn.run(app="irails.core:generate_mvc_app",**kwargs) 
    else:
        _app=generate_mvc_app()
        uvicorn.run(_app,**kwargs)