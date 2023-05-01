import os
from typing import Any, Mapping
from fastapi import BackgroundTasks, Request,Response
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
 
 
from .config import ROOT_PATH,config,_log

env_configs = {} 
static_format = []
def __get_view_configure():
    global static_format,env_configs
    env_options = config.get("view")# {'variable_start_string':'${','variable_end_string':'}'}
    if env_options:
        static_format = env_options.get('static_format',[])
        env_options = env_options.get("jinja2")
        env_configs = env_options.config
     

__get_view_configure()

class _View(object):
    def __init__(self,request,response=None, tmpl_path:str=f"{os.path.abspath('')}/app/views"):
        self._views_directory = tmpl_path
        
        self._templates = Jinja2Templates(directory=self.views_directory,**env_configs)
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

    

    def __call__(self, view_path: str="", context: dict={} ,**kwargs):
        request = self.request
        if not request or not isinstance(request, Request):
            raise ValueError("request instance type must be fastapi.Request") 

        if not view_path.endswith(".html"):
            view_path = f"{view_path}.html"

        context["request"] = request
        try:
            res = self._templates.TemplateResponse(view_path, context,**kwargs)
            return res
        except Exception as e:
            _log.error("template not found"+e.args)
            view_path = os.path.join(self.views_directory,view_path).replace(ROOT_PATH,"").replace("\\","/")
            raise HTTPException(500,f"template not found ![{e.args}]")
        
         
