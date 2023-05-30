# -*- coding: utf-8 -*-
from irails import route, api, Request, Response, BaseController, application
from fastapi.openapi.utils import get_openapi
from fastapi.openapi import docs

application.openapi_url = '/system_admin/admin/swagger'
application.docs_url = '/system_admin/admin/docs'
application.redoc_url = '/system_admin/admin/redoc'


@route(path='/{app}/{controller}', auth='user')
class AdminController(BaseController):
    @api.get('/index')
    def index(self):
        '''
        :title 控制面板
        :nav true
        '''
        return self.vue_sfc_app()
    @api.get("/pages_list")
    def pages_list(self):
        import os
        appinfo = application.apps[self.__app_name__]
        app_dir = self.__appdir__ #'E:\\codedemo\\IRAILS\\apps\\system_admin'
         
        view_dir = os.path.normpath(app_dir+'/views/'+ '/'.join(self.__view_url__.split("/")[2:]))#'/system_admin/admin'


        views_path = os.path.join(view_dir,'pages')
        all_files={}
        for root, dirs, files in os.walk(views_path):
            for file in files:
                name,ext = os.path.splitext(file)
                 
                if ext=='.vue':
                    all_files[name] = f'pages/{file}'
        return all_files

    @api.get('/docs', auth='public', include_in_schema=False)
    def docs(self):
        '''
        :title Api Docs
        '''
        return docs.get_swagger_ui_html(oauth2_redirect_url="/system_admin/user/verity", openapi_url=application.openapi_url, title="API documentation")

    @api.get("/redoc", auth='public', include_in_schema=False)
    def redoc(self):
        '''
        :title Api Redoc
        '''
        return docs.get_redoc_html(openapi_url=application.openapi_url, title="API Redoc")

    @api.get('/swagger', auth='public', include_in_schema=False)
    def swagger(self):
        '''
        :nav false
        '''
        if application.openapi_schema:
            return application.openapi_schema
        openapi_schema = get_openapi(
            title="Custom API",
            version="0.1.0",
            description="This is a custom API",
            routes=application.routes, )
        application.openapi_schema = openapi_schema
        return application.openapi_schema

    @api.get("/app_list")
    def app_list(self):
        '''
        :nav false
        '''
        apps = application.app_list()
        return apps
