import base64
import binascii
import importlib
import os

import casbin
from casbin.enforcer import Enforcer
 
from fastapi import FastAPI,Request,Response
from starlette.authentication import AuthenticationBackend, AuthenticationError, SimpleUser, AuthCredentials,BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import BaseUser,SimpleUser,UnauthenticatedUser
from casbin.persist.adapters import FileAdapter
from casbin.persist.adapter import Adapter
# from .midware_casbin import CasbinMiddleware
 
from .config import config,_log
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple, Type, Union,Dict
from ._utils import iJSONEncoder,is_datetime_format

AUTH_EXPIRED='[EXPIRED]!'

_session_name:str = ""

class CasbinAuth:
    def __init__(self,enforcer:Enforcer,session_name="user") -> None:
        global _session_name
        self.enforcer = enforcer
        self.__session_name = _session_name = session_name
        pass
    def modify_authorization(self,sub,obj,act,authorize:bool):
        """
        :sub(user_name or mainbody),:obj(resource or url),:act(action like 'GET','POST','DELETE')
        add or remove authorization info by :authorzie
        """
        if self.enforcer:
            if authorize:
                return self.enforcer.add_policy(sub,obj,act)
            else:
                return self.enforcer.remove_policy(sub,obj,act)
        raise RuntimeError("Casbin Enforcer is None")
    
    def _auth(self,request:Request,username:str):
        '''
        do verity,return True means `Success` and others `Failed`
        '''
        path = request.url.path
        method = request.method   
        if username:
            user = username
        else:
            user = request.user.display_name if request.user.is_authenticated else 'anonymous'

        return self.enforcer.enforce(user, path, method)
    def __get_token_from_header(self, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError as e:
            raise AuthenticationError('Could not separate Authorization scheme and token') from e 
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token
    def get_user_from_request(self,request:Request,prefix:str="Bearer",is_jwt:bool=False,**kwargs) : 
        userobj = request.session.get(self.__session_name)
        payload = None
        username = ''
       
        if is_jwt:   
            username_field = kwargs['username_field']
            auth = request.headers["Authorization"] if 'Authorization' in request.headers else None
            if auth:
                scheme, credentials = auth.split() 
                token = self.__get_token_from_header(authorization=auth, prefix=prefix)
                
                del kwargs['username_field']
                try:
                    payload = jwt.decode(token,**kwargs)
                except jwt.InvalidTokenError as e:
                    _log.debug('token:'+token + f' has been expired.{e.args}')
                    request.session[self.__session_name] = None
                    return "","",None
                if is_datetime_format(payload['exp']):
                    payload['exp'] = datetime.fromisoformat(payload['exp'])


                return  payload[username_field],token,payload
            elif userobj:
                if 'token' in userobj:
                    try:
                        payload = jwt.decode(userobj['token'],**kwargs)
                    except jwt.InvalidTokenError as e:#Signature has expired
                        request.session[self.__session_name] = None
                        return AUTH_EXPIRED,AUTH_EXPIRED,None
                        # raise AuthenticationError(str(e)) from e
                     
                    return  payload[username_field],userobj['token'],payload
        else:
            if userobj: 
                return userobj,"",None
            else:
                decoded = base64.b64decode(credentials).decode("ascii")
                username, _, password = decoded.partition(":")
                if username:
                    return username,password,None
        return "","",None
    
class AuthenticationBackend_(AuthenticationBackend):
    def create_access_token(self,**kwargs):
        raise NotImplementedError()
    def clear_userinfo(self,request:Request):
        raise NotImplementedError()
    @property
    def casbin_auth(self)->CasbinAuth:
        return _casbin_auth
    pass
class BasicAuth(AuthenticationBackend_):
    def __init__(self,**kwargs) -> None:
        super().__init__()
     
    
    async def authenticate(self, request:Request, **kwargs):
        username,password,_ = _casbin_auth.get_user_from_request(request=request)
        if not username:
            return False,None
        user = SimpleUser(username)
        request.scope['user'] = user
        auth_type:str = kwargs.get("auth_type")
        if not auth_type or auth_type.lower()=='public': 
            return True,  user
        result = _casbin_auth._auth(request=request,username=username)
        return result, user

         
    def clear_userinfo(self,request:Request):
        global _session_name
        del request.session[_session_name] 
        
    def create_access_token(self,  username,**kwargs):
        global _session_name
        request:Request = kwargs['request'] if 'request' in kwargs else None
        if request:
            request.session[_session_name] = username
        return None
        
class JWTUser(BaseUser):
    def __init__(self, username: str, token: str, payload: dict) -> None:
        self.username = username
        self.token = token
        self.payload = payload

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class JWTAuthenticationBackend(AuthenticationBackend_):

    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'HS256',
                 prefix: str = 'Bearer',
                 username_field: str = 'username',
                 audience: Optional[str] = None,
                 options: Optional[dict] = None) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field
        self.audience = audience
        self.options = options or dict()
    
     
    
    async def authenticate(self, request,**kwargs) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        auth_type:str = kwargs.get("auth_type")

        args = {'username_field':self.username_field, 'key':self.secret_key, 'algorithms': self.algorithm , 'audience':self.audience ,
                                            'options':self.options }
        userobj,token,payload = _casbin_auth.get_user_from_request(request=request,
                                                                 prefix=self.prefix, 
                                                                 is_jwt=True,**args)
        if token==AUTH_EXPIRED:
            return False,AUTH_EXPIRED
         
        user = userobj#SimpleUser(userobj['username'])
        request.scope['user'] = user
        if  auth_type.lower()=='public': 
            if userobj:
                if hasattr(userobj,'token') or token or payload:
                    if payload and token:
                        request.scope['user'] = JWTUser(username=payload[self.username_field], token=token,
                                                        payload=payload)  
                        return True, request.scope['user']
            
            return False,None #auth public must login
           
        if  payload:
            user = JWTUser(username=payload[self.username_field], token=token,
                                                        payload=payload) 
            request.scope['user'] = user
            result = _casbin_auth._auth(request=request,username=payload[self.username_field])
            
            return result, user  
        return False,None
    def clear_userinfo(self,request:Request):
        global _session_name
        if _session_name in request.session:
            del request.session[_session_name] 
    def create_access_token(self,  user , expires_delta: timedelta = None,**kwargs)  :
        global _session_name
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            authCfg = config.get('auth')
            if authCfg:
                expires_delta = int(authCfg.get('expires_delta',60))
            else:
                expires_delta = 60
            expire = datetime.utcnow() + timedelta(
                minutes=expires_delta
            )
        if isinstance(user,str):
            userObj = {"exp": expire, "username": user }
        elif isinstance(user,JWTUser):
            userObj = {"exp": expire, "username": user.username}
        elif isinstance(user,BaseUser):
            userObj = {"exp": expire, "username": user.display_name}
        request:Request = kwargs['request']
        
        access_token = jwt.encode(userObj, self.secret_key ,self.algorithm )
        userObj.update({"token":access_token})
        request.session[_session_name] = userObj
        return access_token
    
_casbin_auth:CasbinAuth = None

def init(app:FastAPI,backend:AuthenticationBackend,adapter_class:Type=None,**kwagrs)->AuthenticationBackend:
    """
        kwargs:secret_key=KEY
    """
    __session_name = config.get("auth").get("session_name",'user')
    global _casbin_auth
    cfg = config.get("auth")
    adapter_uri = kwagrs.get('adapter_uri',None)
    del kwagrs['adapter_uri']
    model_file = cfg.get("auth_model",'./configs/casbin-model.conf')    
    adapter = adapter_class(adapter_uri)
    enforcer = casbin.Enforcer(model_file, adapter)
   
    _casbin_auth = CasbinAuth(enforcer=enforcer,session_name=__session_name)
    
    return backend(**kwagrs) 
def reload_adapter(app:FastAPI,adapter:Adapter=None):
    cfg = config.get("auth")
    model_file = cfg.get("auth_model",'./configs/casbin-model.conf')    
    if not adapter:
        adapter_file = cfg.get("auth_adapter",'./configs/casbin-adapter.csv')    
        adapter = FileAdapter(adapter_file)   
    enforcer = casbin.Enforcer(model_file, adapter) 
    app.router.current_casbin_instance = enforcer

def get_auth_backend(name:str)->AuthenticationBackend: 
    _auth_types = {'basic':BasicAuth,'jwt':JWTAuthenticationBackend}
    return _auth_types[name] if name in  _auth_types else None

def get_adapter_module(name:str)->Adapter:
    from ._loader import load_module
    if name.lower()=='file':
        return FileAdapter
    module_name= f"{name}_adapter"
    module_dir = os.path.dirname(__file__)
    module_dir = os.path.join(module_dir,'casbin_adapters')
    module_path = os.path.join(module_dir, module_name + '.py') 
    module = load_module(module_name,module_path)
    if module and hasattr(module,'Adapter'):
        return getattr(module,'Adapter')   
    else:
        raise RuntimeError("Can't load module:{module_path}")
 