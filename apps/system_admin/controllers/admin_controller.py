# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
from fastapi.openapi.utils import get_openapi 
from fastapi.openapi import docs

application.openapi_url = '/system_admin/admin/swagger'
application.docs_url = '/system_admin/admin/docs'
application.redoc_url = '/system_admin/admin/redoc'

@route(path='/{app}/{controller}',auth='user')
class AdminController(BaseController):  
    @api.get('/index')
    def index(self):
        '''
        :title 控制面板
        :nav true
        '''
        return self.view()            
    @api.get('/docs',auth='public',include_in_schema=False)
    def docs(self):
        '''
        :title Api Docs
        '''
        return docs.get_swagger_ui_html(openapi_url=application.openapi_url, title="API documentation")

    @api.get("/redoc",auth='public',include_in_schema=False)
    def redoc(self):
        '''
        :title Api Redoc
        '''
        return docs.get_redoc_html(openapi_url=application.openapi_url,title="API Redoc")
         
    @api.get('/swagger',auth='public',include_in_schema=False)
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
        import copy
        apps = []
        for app_name in application.apps:
            manifest=copy.copy(application.apps[app_name]['manifest'])
            route_map = copy.copy(application.apps[app_name]['route_map'])
            for item in route_map:
                if 'endpoint' in route_map[item]:
                    del route_map[item]['endpoint']
            funcs = []
            for item in route_map:
                _item = route_map[item]
                _item.update({'function':item})
                funcs.append(_item)
            manifest.update({'app_name':app_name,'routes':funcs})
             
            apps.append(manifest)

        return apps