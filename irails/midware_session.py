import json
import sys
import typing,uuid
from typing import Dict
from base64 import b64decode, b64encode
from ._i18n import _
import itsdangerous
from itsdangerous.exc import BadSignature

from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from .log import _log
from .base_controller import _session_key
if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal
from ._utils import iJSONEncoder,is_datetime_format

class SessionStorage(): 
    def __init__(self) -> None:  
        super().__init__()
     
    def get(self, session_id: str) :
        raise NotImplementedError
        pass 
    def set(self, session_id: str, data ) -> None:
        raise NotImplementedError 
    def delete(self, session_id: str) -> None:
        raise NotImplementedError
class MemoryStorage(SessionStorage):
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str)  :
        return self.sessions.get(session_id, {})

    def set(self, session_id: str, data ) -> None:
        self.sessions[session_id] = data

    def delete(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)   
import os
class FileStorage(SessionStorage):
    filename:str = ""
    cachedData:Dict[str,Dict] = {}

    def __init__(self, dir: str ):
        
        super().__init__( )
        self._dir = dir
        
        if not os.path.exists(dir):
            os.mkdir(dir)

    def ensure_file_exists(self,sid,type='set' ):
        if not os.path.exists(self._dir):
            os.mkdir(self._dir)
        filename = os.path.join(self._dir , sid)
        if not os.path.exists(filename) :
            if type=='set':
                with open(filename,"w") as file:
                    file.write("")
            else:
                return False
        return filename
 
     
    def get(self, session_id: str)  :
        filename = self.ensure_file_exists(session_id,'get')
        if not filename: return b''
        if session_id in self.cachedData:
            return self.cachedData[session_id]
        try:
            with open(filename, "rb") as f:
                data = f.read() 
            self.cachedData[session_id] = data
        except FileNotFoundError:
            data = b""
        except Exception as e:
            _log.error(e)
            data = b""
        return data

    def set(self, session_id: str, data ) -> None:
        filename = self.ensure_file_exists(session_id)
        self.cachedData[session_id] = data 
        with open(filename, "wb") as f:
            f.write(data)

    def delete(self, session_id: str) -> None:
        filename = self.ensure_file_exists(session_id,'delete')
        try:
            if filename:
                os.remove(filename)
        except Exception as e:
            _log.error(e)   

try:
    import redis
    class RedisStorage(SessionStorage):
        def __init__(self, host: str, port: int, password: str, db: int): 
            self.redis_client = redis.Redis(host=host, port=port, password=password, db=db)

        def get(self, session_id: str) -> Dict:
            data = self.redis_client.get(session_id)
            if data is None:
                return {}
            return json.loads(data)

        def set(self, session_id: str, data: Dict) -> None:
            self.redis_client.set(session_id, json.dumps(data,cls=iJSONEncoder))

        def delete(self, session_id: str) -> None:
            self.redis_client.delete(session_id)
except(ImportError):
    class RedisStorage(SessionStorage):
        def __init__(self, k: str = "") -> None:
            raise ImportError("redis seen is not installed,please use `pip install redis` to install it.")
    pass

 
class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        
        secret_key: typing.Union[str, Secret],
        storage:SessionStorage = None,
        session_cookie: str = _session_key,
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ) -> None:
        self.app = app
        self.signer = itsdangerous.TimestampSigner(str(secret_key))
        self.storage = storage
        self.session_cookie_key = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True
        
        if self.session_cookie_key in connection.cookies:
            if self.storage:
                data = self.storage.get(connection.cookies[self.session_cookie_key])
            else:
                data = connection.cookies[self.session_cookie_key].encode("utf-8")
            try:
                data = self.signer.unsign(data, max_age=self.max_age)
                scope["session"] =  (json.loads(b64decode(data)))
                initial_session_was_empty = False
            except BadSignature:
                if self.storage:
                    self.storage.delete(connection.cookies[self.session_cookie_key])
                scope["session"] = {}
        else:
            
            scope["session"] = {}
        # old_data = scope["session"].copy()

        async def send_wrapper(message: Message) -> None: 
            if self.storage is None:
                if message["type"] == "http.response.start":
                    if scope["session"]:
                        # We have session data to persist.
                        data = b64encode(json.dumps(scope["session"],cls=iJSONEncoder).encode("utf-8"))
                        data = self.signer.sign(data)
                        headers = MutableHeaders(scope=message)
                        header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                            session_cookie=self.session_cookie_key,
                            data=data.decode("utf-8"),
                            path=self.path,
                            max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                            security_flags=self.security_flags,
                        )
                        headers.append("Set-Cookie", header_value)
                    elif not initial_session_was_empty:
                        # The session has been cleared.
                        headers = MutableHeaders(scope=message)
                        header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                            session_cookie=self.session_cookie_key,
                            data="null",
                            path=self.path,
                            expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                            security_flags=self.security_flags,
                        )
                        headers.append("Set-Cookie", header_value)
            else:
                if message["type"] == "http.response.start":
                    

                    data = b64encode(json.dumps(scope["session"],cls=iJSONEncoder).encode("utf-8"))
                    data = self.signer.sign(data)
                    # data = data.decode("utf-8")
                    
                        # The session has not been inited.
                    def find_session_id():
                        for key,content in message['headers']:
                            if key==b'set-cookie' and content.startswith(bytes(self.session_cookie_key,'utf-8')):
                                return str(content,'utf-8').split(";")[0].split("=")[1]
                        
                        for key,content in scope['headers']:
                            if key==b'cookie' and content.startswith(bytes(self.session_cookie_key,'utf-8')):
                                return str(content,'utf-8').split(";")[0].split("=")[1]
                        
                    sid = find_session_id()    
                    #storage
                    if sid:     
                        self.storage.set(sid,data)
                
            await send(message)

        await self.app(scope, receive, send_wrapper)

_SESSION_STORAGES = {"file":FileStorage,"memory":MemoryStorage,'redis':RedisStorage}