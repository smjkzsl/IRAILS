import base64

import os

import casbin
from casbin.enforcer import Enforcer

from fastapi import FastAPI, Request, Response
from starlette.authentication import AuthenticationBackend, AuthenticationError, SimpleUser, AuthCredentials, BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import BaseUser, SimpleUser, UnauthenticatedUser
from casbin.persist.adapters import FileAdapter
from casbin.persist.adapter import Adapter
# from .midware_casbin import CasbinMiddleware

from .config import config, ROOT_PATH
from .log import _log
import jwt
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Type, Union, Dict
from ._utils import iJSONEncoder, is_datetime_format
from ._i18n import _
AUTH_EXPIRED = '[EXPIRED]!'
_session_name: str = ""
default_domain = "system"

cfg = config.get("auth")
super_domain = cfg.get('super_domain', 'system')
super_group = cfg.get('super_group', 'admin')
casbin_enforcer: Enforcer = None
_casbin_auth: 'CasbinAuth' = None

def is_super(username, domain, *args, **kwargs):
    roles = casbin_enforcer.get_roles_for_user_in_domain(username, super_domain)
    super_users = casbin_enforcer.get_users_for_role_in_domain(
        super_group, super_domain)  # ['root', 'bruce']

    return super_group in roles and username in super_users


class DomainUser(BaseUser):
    def __init__(self, username: str = 'anonymous', roles=[], domain: str = "") -> None:
        '''
        :group Roles 
        :domain Tenant
        '''
        self.username = username
        self._roles = roles
        self._domain = domain or default_domain
        self._lang = "zh"
        self._timezone = 'Asia/Shanghai'
        super().__init__()

    @property
    def roles(self):
        return self._roles

    def set_roles(self, value: List):
        names = []
        for row in value:
            names.append(row.name)
        self._roles = names

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        if not value:
            value = default_domain
        self._domain = value

    @property
    def is_authenticated(self) -> bool:
        return self.username != 'anonymous'

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        identity = self.username
        if self._roles:
            group = self._roles
            if self._domain:
                group = self._domain+"." + ','.join(group)
            identity += '@'+group
        return identity

    def __repr__(self):
        return self.identity


class BasicUser(DomainUser):
    def __init__(self, username: str, group: str = "", domain: str = "") -> None:
        super().__init__(username, group, domain)


class JWTUser(DomainUser):
    def __init__(self, username: str, token: str, payload: dict, group: str = "", domain: str = "") -> None:
        self.token = token
        self.payload = payload
        super().__init__(username, group, domain)


class CasbinAuth:
    def __init__(self, enforcer: Enforcer, session_name="user") -> None:
        global _session_name
        self.enforcer = enforcer
        self.__session_name = _session_name = session_name
        pass

    def policy(self, *args, **kwargs):
        """
        :sub(user_name or mainbody),:obj(resource or url),:act(action like 'GET','POST','DELETE')
        add or remove authorization info by :authorzie
        """
        authorize = True
        if kwargs and 'authorize' in kwargs:
            authorize = kwargs['authorize']
        if self.enforcer:
            if authorize:
                return self.enforcer.add_policy(*args)
            else:
                return self.enforcer.remove_policy(*args)
        raise RuntimeError("Casbin Enforcer is None")

    def grouping(self, *args, **kwargs):
        '''grouping(`alice`,`admin`) add `alice` to group `admin` or delete it'''
        authorize = True
        if kwargs and 'authorize' in kwargs:
            authorize = kwargs['authorize']
        if self.enforcer:
            if authorize:
                return self.enforcer.add_grouping_policy(*args)
            else:
                return self.enforcer.remove_grouping_policy(*args)
        raise RuntimeError("Casbin Enforcer is None")

    def is_grouping(self, *args):
        ''' is_grouping('alice','admin')? return `alice` is belongs `admin` '''
        if self.enforcer:
            return self.enforcer.has_grouping_policy(*args)
        raise RuntimeError("Casbin Enforcer is None")

    def _auth(self, request: Request, user: DomainUser):
        '''
        do verity,return True means `Success` and others `Failed`
        '''
        if not user.roles:
            raise RuntimeError(_("User must have a role %s") % user)
        sub = user.username
        dom = user.domain
        obj = request.url.path
        act = request.method

        return self.enforcer.enforce(sub, dom, obj, act)

    def __get_token_from_header(self, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError as e:
            raise AuthenticationError(
                _('Could not separate Authorization scheme and token')) from e
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(
                _('Authorization scheme %s is not supported') % {scheme})
        return token

    def get_user_from_request(self, request: Request, prefix: str = "Bearer", is_jwt: bool = False, **kwargs):
        userobj = request.session.get(self.__session_name)
        payload = None
        username = ''

        if is_jwt:
            username_field = kwargs['username_field']
            auth = request.headers["Authorization"] if 'Authorization' in request.headers else None
            if auth:
                scheme, credentials = auth.split(' ')
                try:
                    token = self.__get_token_from_header(
                        authorization=auth, prefix=prefix)

                    del kwargs['username_field']

                    payload = jwt.decode(token, **kwargs)
                except AuthenticationError as e:
                    return "", "", None
                except jwt.InvalidTokenError as e:
                    msg = _('token %s has been expired(%s)' % (token, e.args))
                    _log.debug(msg)
                    request.session[self.__session_name] = None
                    return "", "", None
                if is_datetime_format(payload['exp']):
                    payload['exp'] = datetime.fromisoformat(payload['exp'])

                return payload[username_field], token, payload
            elif userobj:
                if 'token' in userobj:
                    try:
                        payload = jwt.decode(userobj['token'], **kwargs)
                    except jwt.InvalidTokenError as e:  # Signature has expired
                        request.session[self.__session_name] = None
                        return AUTH_EXPIRED, AUTH_EXPIRED, None
                        # raise AuthenticationError(str(e)) from e

                    return payload[username_field], userobj['token'], payload
        else:
            if userobj:
                return userobj, "", None
            else:
                decoded = base64.b64decode(credentials).decode("ascii")
                username, _, password = decoded.partition(":")
                if username:
                    return username, password, None
        return "", "", None


class AuthenticationBackend_(AuthenticationBackend):
    user_class = DomainUser

    def create_access_token(self, **kwargs):
        raise NotImplementedError()

    def clear_userinfo(self, request: Request):
        raise NotImplementedError()

    @property
    def casbin_auth(self) -> CasbinAuth:
        return _casbin_auth


class BasicAuth(AuthenticationBackend_):

    def __init__(self, **kwargs) -> None:

        super().__init__()

    async def authenticate(self, request: Request, **kwargs):
        userobj, password, _ = _casbin_auth.get_user_from_request(
            request=request)
        if not userobj:
            return False, None
        if isinstance(userobj, BasicUser):
            user = userobj
        elif isinstance(userobj, str):
            user = BasicUser(userobj)
        request.scope['user'] = user
        auth_type: str = kwargs.get("auth_type")
        if not auth_type or auth_type.lower() == 'none':
            return True,  user
        elif auth_type.lower() == 'public':
            return user.is_authenticated, user
        elif not user.is_authenticated:
            return False.user
        else:
            result = _casbin_auth._auth(request=request, user=user)

        return result, user

    def clear_userinfo(self, request: Request):
        global _session_name
        del request.session[_session_name]

    def create_access_token(self,  user: DomainUser, **kwargs):
        global _session_name
        request: Request = kwargs['request'] if 'request' in kwargs else None
        if request:
            request.session[_session_name] = user
        return None


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

    async def authenticate(self, request: Request, **kwargs) -> Union[None, Tuple[AuthCredentials, JWTUser]]:
        auth_type: str = kwargs.get("auth_type")

        _kwargs = {'username_field': self.username_field, 
                'key': self.secret_key, 
                'algorithms': self.algorithm, 
                'audience': self.audience,
                'options': self.options}
        user_name, token, payload = _casbin_auth.get_user_from_request(request=request,
                                                                       prefix=self.prefix,
                                                                       is_jwt=True, **_kwargs)
        if token == AUTH_EXPIRED:
            self.clear_userinfo(request)
            return False, AUTH_EXPIRED
        jwtuser: BasicUser = DomainUser()

        def from_payload(payload) -> JWTUser:
            return JWTUser(username=payload[self.username_field],
                           token=token,
                           group=payload['group'],
                           domain=payload['domain'],
                           payload=payload)
        if user_name or token or payload:
            if payload and token:
                jwtuser = from_payload(payload)
                request.scope['user'] = jwtuser

        if auth_type.lower() == 'public':
            return jwtuser.is_authenticated, jwtuser
        elif auth_type.lower() == 'none':
            return True, jwtuser
        elif not jwtuser.is_authenticated:
            return False, jwtuser
        else:
            result = _casbin_auth._auth(request=request, user=jwtuser)
        return result, jwtuser

    def clear_userinfo(self, request: Request):
        global _session_name
        if _session_name in request.session:
            del request.session[_session_name]

    def create_access_token(self,  user: DomainUser, expires_delta: timedelta = None, **kwargs):
        global _session_name
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            authCfg = config.get('auth')
            if authCfg:
                expires_delta = int(authCfg.get('expires_delta', 60))
            else:
                expires_delta = 60
            expire = datetime.utcnow() + timedelta(
                minutes=expires_delta
            )

        auth_user_obj = {
            "exp": expire,
            "username": user.username,
            "group": user.roles,
            "domain": user.domain
        }

        request: Request = kwargs['request']

        access_token = jwt.encode(
            auth_user_obj, self.secret_key, self.algorithm)
        auth_user_obj.update({"token": access_token})
        request.session[_session_name] = auth_user_obj
        return access_token





def init(app: FastAPI, backend: AuthenticationBackend, adapter_class: Type = None, **kwagrs) -> AuthenticationBackend:
    """
        kwargs:secret_key=KEY
    """
    __session_name = config.get("auth").get("session_name", 'user')
    global _casbin_auth, casbin_enforcer

    adapter_uri = kwagrs.get('adapter_uri', None)

    del kwagrs['adapter_uri']
    model_file = cfg.get("auth_model", './configs/casbin-model.conf')
    if not os.path.isabs(model_file):
        model_file = os.path.abspath(os.path.join(ROOT_PATH, model_file))
    if not os.path.exists(model_file):
        raise RuntimeError(
            _("Casbin model file %s does not exists!") % model_file)

    if adapter_class is FileAdapter and not os.path.isabs(adapter_uri):
        adapter_uri = os.path.abspath(os.path.join(ROOT_PATH, adapter_uri))
    adapter = adapter_class(adapter_uri)
    from casbin.model import Model
    model = Model()
    with open(model_file, 'r', encoding='utf-8') as f:
        model_content = f.read()
        # if super_user and super_group:
        #     model_content = model_content.replace("${super_user}",super_user).replace("${super_group}",super_group)
        model.load_model_from_text(model_content)
    casbin_enforcer = casbin.Enforcer(model, adapter)
    casbin_enforcer.add_function('is_super', is_super)
     
    _casbin_auth = CasbinAuth(enforcer=casbin_enforcer, session_name=__session_name)

    return backend(**kwagrs)


def get_auth_backend(name: str) -> AuthenticationBackend_:
    _auth_types = {'basic': BasicAuth, 'jwt': JWTAuthenticationBackend}
    return _auth_types[name] if name in _auth_types else None


def get_adapter_module(name: str) -> Adapter:
    from ._loader import load_module
    if name.lower() == 'file':
        return FileAdapter
    module_name = f"{name}_adapter"
    module_dir = os.path.dirname(__file__)
    module_dir = os.path.join(module_dir, 'casbin_adapters')
    module_path = os.path.join(module_dir, module_name + '.py')
    module = load_module(module_name, module_path)
    if module and hasattr(module, 'Adapter'):
        return getattr(module, 'Adapter')
    else:
        raise RuntimeError(_("Can't load module:%s") % module_path)
