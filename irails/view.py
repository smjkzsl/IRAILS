import os
from typing import Any, Mapping
from fastapi import BackgroundTasks, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
import jinja2

from .config import ROOT_PATH, config
from .log import _log
from ._i18n import _
env_configs = {}
static_format = []


def get_view_configure():
    global static_format, env_configs
    # {'variable_start_string':'${','variable_end_string':'}'}
    env_options = config.get("view")
    if env_options:
        static_format = env_options.get('static_format', [])
        env_options = env_options.get("jinja2")
        env_configs = env_options.config

    return env_configs

get_view_configure()


class _View(object):
    def __init__(self, request, response=None, tmpl_path: str = f"{os.path.abspath('')}/app/views"):
        self._views_directory = tmpl_path

        self._templates = Jinja2Templates(
            directory=self.views_directory, **env_configs)
        self.request = request
        self.response = response

    @property
    def templates(self):
        return self._templates

    @property
    def views_directory(self):
        return self._views_directory

    @views_directory.setter
    def views_directory(self, views_directory: str):
        self._views_directory = views_directory
        self._templates = Jinja2Templates(directory=self.views_directory)

    def __call__(self, view_path: str = "", context: dict = {}, **kwargs):
        request = self.request
        if not request or not isinstance(request, Request):
            raise ValueError(
                _("request instance type must be fastapi.Request"))

        if not view_path.endswith(".html"):
            view_path = f"{view_path}.html"

        context["request"] = request
        view_path_real = os.path.join(self.views_directory, view_path).replace(
            ROOT_PATH, "").replace("\\", "/")
        try:
            res = self._templates.TemplateResponse(
                view_path, context, **kwargs)
            return res
        except jinja2.exceptions.TemplateSyntaxError as e:
            source = e.source.split('\n')[e.lineno-1:e.lineno]
            info = _("TemplateSyntaxError on %s :line:%s ,%s") % (
                view_path_real, e.lineno, source)
            _log.error(info)
            raise HTTPException(500, info)
        except jinja2.exceptions.TemplateNotFound as e:
            source = e.args[0]
            info = _("%s raised TemplatesNotFound Error: `%s`") % (
                view_path_real, source)
            _log.error(info)
            raise HTTPException(500, info)
        except jinja2.exceptions.UndefinedError as e:
            info = _("Tempate %s raised Exception %s") % (
                view_path_real, e.args)
            _log.error(info)

            raise HTTPException(500, info)
        except Exception as e:
            info = _("Tempate %s raised Exception %s") % (
                view_path_real, e.args)
            _log.error(info)

            raise HTTPException(500, info)
