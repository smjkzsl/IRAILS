# -*- coding: utf-8 -*-
from irails import route, api, Request, Response, BaseController, application
from fastapi.openapi.utils import get_openapi
from fastapi.openapi import docs
from irails._i18n import _

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
        return self.vue_sfc_app(title="Admin")

    @api.get("/pages_list")
    def pages_list(self):
        '''
        :nav false
        '''
        import os
        appinfo = application.apps[self.__app_name__]
        app_dir = self.__appdir__  # 'E:\\codedemo\\IRAILS\\apps\\system_admin'

        view_dir = os.path.normpath(
            app_dir+'/views/' + '/'.join(self.__view_url__.split("/")[2:]))  # '/system_admin/admin'

        # {
        #     '.':
        #         ['a.vue','b.vue'],
        #     'system':
        #         ['cc.vue','dd.vue'],
        # }

        views_path = os.path.join(view_dir, 'pages')
        all_files = {}
        for root, dirs, files in os.walk(views_path):
            for file in files:
                name, ext = os.path.splitext(file)
                _dirs = os.path.relpath(root, views_path)
                _dir_name = _dirs
                if not _dir_name in all_files:
                    all_files[_dir_name] = []
                if ext == '.vue':
                    title = self._(file)
                    all_files[_dir_name].append({'file':file,'title':title})

                    # all_files[name] = {'dir_name':_dirs,'file_path': f'pages/{_dirs}{file}'}
        return all_files

    @api.get('/docs', auth='public', include_in_schema=False)
    def docs(self):
        '''
        :title Api Docs
        '''
        return docs.get_swagger_ui_html(oauth2_redirect_url="/system_admin/user/verity",
                                         openapi_url=application.openapi_url, 
                                         title="API documentation")

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
        t = self.params('t','installed') 
        apps = application.app_list()
        if t == 'installed': 
            for item in apps:
                item['is_installed'] = True
        elif t:
            from irails._loader import collect_apps 
            all_apps = collect_apps(do_load=False,application=application) 
            ret = []
            for item in all_apps:
                manifest = item['manifest']
                manifest['app_name'] = item['package']
                manifest['is_installed'] = item['package'] in application.apps
                if manifest['is_installed']:
                    for app in apps:
                        if app['app_name'] == item['package']:
                            manifest['routes'] = app['routes']
                if t=='all':
                    ret.append(manifest)
                elif t=='uninstalled' and not manifest['is_installed']:
                    ret.append(manifest)
            apps = ret
        return apps

    @api.post("/uninstall")
    def uninstall(self):
        app_name = self['app_name']
        if app_name:
            from irails._utils import  enable_app
            from irails._loader import _unload_app 
            if enable_app(app_name,False): 
                if _unload_app(application=application,app_name=app_name):
                    return 'OK'
        return 'Failed'
        
    @api.post("/install")
    def install(self):
        app_name = self.params('app_name')
        if app_name:
            from irails._loader import _load_app,collect_apps 
            from irails._utils import enable_app
            from irails.core import _register_controllers,check_db_migrate
            from irails.midware import mount_app_statics
            from irails.config import debug
            import os
            all_apps = collect_apps(do_load=False,application=application) 
            for app in all_apps:
                if app['package']==app_name:
                    app_dir = app['app_dir']
                    if not os.path.isabs(app_dir):
                        app_dir = os.path.abspath(app_dir)
                    app_dir = os.path.dirname(app_dir)
                    n=_load_app(app_dir,app_name,app['manifest'])

                    if n and app_name in application.apps:
                        application.apps[app_name]['manifest'] = app['manifest']
                        _register_controllers()
                        mount_app_statics(application,app_name,debug)
                        check_db_migrate()
                        enable_app(app_name)
                        return 'OK'
        return 'Failed'