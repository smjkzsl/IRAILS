from typing import List, Tuple

import os
import time
import typing
from fastapi import FastAPI, HTTPException, exceptions, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import Scope
from starlette.staticfiles import PathLike
from fastapi.middleware import Middleware
from starlette.middleware import Middleware as StarletteMiddleware
from starlette.types import Receive, Scope, Send
import jinja2
import chardet

from .config import config, ROOT_PATH
from .log import get_logger
from .midware_session import (SessionMiddleware, FileStorage,
                              MemoryStorage, RedisStorage, SessionStorage, _SESSION_STORAGES)

from .view import _View, env_configs, static_format
from .config import config, ROOT_PATH
from ._i18n import _

_log = get_logger(__name__)

errors = config.get("errors")
if errors:
    error_404 = errors.get('error_404_page')
    error_500 = errors.get("error_500_page")
    disabled_path_of_files = [os.path.abspath(error_404),
                              os.path.abspath(error_500),
                              ]
else:
    disabled_path_of_files = []


class MvcStaticFiles(StaticFiles):

    def file_response(self,full_path: PathLike,stat_result: os.stat_result,scope: Scope,status_code: int = 200,) -> Response:

        if full_path in disabled_path_of_files:
            return Response(None, 404)
        ext = full_path.split(".")[-1] if full_path.find(".") > -1 else ""
        if ext and ext in static_format: 
            context = {"request": Request(scope)}
            with open(full_path, 'rb') as f:
                bstr = f.read()
                result = chardet.detect(bstr)
                content = bstr.decode(result['encoding'])

            tmp = jinja2.Template(source=content, **env_configs)
            txt = tmp.render(context)
            return Response(txt)
        else:
            scope['root_path'] = scope['root_path'] + scope['path']
            return super().file_response(full_path,stat_result,scope,status_code=status_code,)

def mount_app_statics(app,app_name,debug=False):
    __roots = {}
    _msg = []
    for _dir in app.apps[app_name]['view_dirs']: 
        _url: str = app.apps[app_name]['view_dirs'][_dir]
        _url = '/'+_url if not _url.startswith('/') else _url 
        _dir = os.path.normpath(_dir)
        if os.path.exists(_dir):
            if _url == '/':
                __roots[_dir] = _url
            else:
                _url = _url.lower() + "/" if not _url.endswith("/") else _url.lower()
                     
                _msg.append(f"PATH:{_dir} =>[URL]: {_url}")
                app.mount(_url, MvcStaticFiles(directory=_dir), name=_dir)
        else:
            _msg.append(f"PATH:{_dir} do not exists!skiped.")
    #mount app static locales dir
    _locales_dir = os.path.normpath(app.apps[app_name]['app_dir'] + '/views/locales')
    if os.path.exists(_locales_dir):
        
        _url = f"/{app_name}/locales"

        app.mount(_url, MvcStaticFiles(directory=_locales_dir), name=_locales_dir)
        _msg.append(f"PATH:{_locales_dir} => [URL]: {_url}")
    if debug:
        
        _log.info("\n" + "\n".join(_msg))
    return __roots

def mount_statics(app, debug=False):
    __roots = {}
    root_app = ""
    for app_name in app.apps:
        
        app__roots = mount_app_statics(app,app_name,debug)
        if not __roots and app__roots:
            __roots = app__roots
            root_app = app_name
        elif root_app and app__roots :
            raise RuntimeError("Mount statics error,Duplicate definition of ROOT(`/`) path,`{root_app}` already defined")
    # mount public resources
    public_dir = config.get("public_dir")
    public_dir = os.path.abspath(os.path.join(ROOT_PATH, public_dir))
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
    app.mount('/public/',  MvcStaticFiles(directory=public_dir), name='public')

    if config.get("upload"):
        updir = config.get("upload")['dir'] or "uploads"
    else:
        updir = 'uploads'

    if os.path.exists(updir):
        app.mount('/uploads/',  StaticFiles(directory=updir), name='uploads')
    # root mount must the last
    for _dir in __roots:
        if debug:
            _log.info(f"StaticDir:{_dir} mounted: {__roots[_dir]}")
        app.mount(__roots[_dir], MvcStaticFiles(directory=_dir), name=_dir)


def init(app: FastAPI, debug: bool = False):
    cors_cfg = config.get("cors")
    if cors_cfg:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_cfg.get('allow_origins'),
            allow_credentials=cors_cfg.get("allow_credentials"),
            allow_methods=cors_cfg.get("allow_methods", ["*"]),
            allow_headers=cors_cfg.get("allow_headers", ["*"]),
        )

    mount_statics(app=app, debug=debug)

    # session midware
    _session_cfg: typing.Dict = config.get("session")
    _session_options = {}
    if _session_cfg:
        _storageType = _session_cfg.get("type", "")
        if _storageType != "":
            if _storageType == 'file':
                _session_options["storage"] = _SESSION_STORAGES[_storageType](
                    dir=_session_cfg.get("dir", "./sessions"))
            else:
                _session_options["storage"] = _SESSION_STORAGES[_storageType]()

        _session_options['secret_key'] = _session_cfg.get("secret_key", "")
    app.add_middleware(SessionMiddleware, **_session_options)

    def error_page(code: int, request, e):
        page = config.get(f"error_page")
        if page:
            page = page.get(f"page_{code}")
        if page and os.path.exists(page):
            viewObj = _View(request=request, response=None,
                            tmpl_path=os.path.abspath(os.path.dirname(page)))
            file = os.path.basename(page)
            content = []
            if debug:
                exc_traceback = e.__traceback__
                # show traceback the last files and location
                tb_summary = traceback.extract_tb(exc_traceback)

                for filename, line, func, text in tb_summary:
                    content.append(f"{filename}:{line} in {func}")

            context = {'error': e, 'debug': debug, 'debug_info': content}

            return viewObj(file, context, status_code=404)
        return None

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, e: StarletteHTTPException):
        e_no = 404
        e_info=""
        if e.args and isinstance(e.args, tuple):
            e_no = e.args[0]
            if debug:
                e_info = str(e.args[1])
        elif e.args:
            e_info = str(e.args)
        ret = error_page(e_no, request=request, e=e)
        if ret:
            return ret
        else:
            content = "<h1>404 Not Found(URL Exception)</h1>"
            content += '<h3>'+_('please check URL of your input!')+'</h3>'
            if debug and e_info:
                content += '<p>' + str(e_info) + '</p>'
            return HTMLResponse(content=content, status_code=404)

    @app.exception_handler(Exception)
    async def validation_exception_handler(request, e: Exception):
        ret = error_page(500, request=request, e=e)
        if ret:
            return ret
        else:
            content = "<h1>500 Internal Server Error</h1>"
            if debug:
                exc_traceback = e.__traceback__
                # show traceback the last files and location
                tb_summary = traceback.extract_tb(exc_traceback)
                content += '<p>'
                for filename, line, func, text in tb_summary:
                    content += (f"{filename}:{line} in {func}</br>")
                content += '</p>'
                content += '<p>Error description:' + str(e.args) + '</p>'
            return HTMLResponse(content=content, status_code=500)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        _log.error(f"OMG! The client sent invalid data!: {exc}")
        return await request_validation_exception_handler(request, exc)

    # denied to access error page for directly
    # @app.route('/public/error_404.html',['GET','POST','HEAD','OPTION','PUT','DELETE'])
    # def _error1(request):
    #     raise HTTPException(404,"Not Found.")
    # @app.route('/public/error_500.html',['GET','POST','HEAD','OPTION','PUT','DELETE'])
    # def _error2(request):
    #     raise HTTPException(404,"Not Found.")

    # @app.get("/favicon.ico")
    # def _get_favicon():
    #     if os.path.exists("./public/favicon.ico"):
    #         return FileResponse("./public/favicon.ico")
    #     else:
    #         return Response(content = None,status_code= 404)

    if debug:
        @app.middleware("http")
        async def preprocess_request(request: Request, call_next):
            start_time = time.time()
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
