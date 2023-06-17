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
                if name.startswith("_") :
                    continue
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
            pass
        elif t:
            from irails._loader import collect_apps 
            all_apps = collect_apps(do_load=False,application=application) 
            ret = []
            for item in all_apps:
                manifest = item['manifest']
                app_name = item['package']
                manifest['app_name'] = app_name
                manifest['is_installed'] = app_name in application.apps and application.apps[app_name]['is_installed']
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
    def get_all_app_names(self)->'list':
        from irails._loader import collect_apps 
        all_apps = collect_apps(do_load=False,application=application) 
        ret = []
        for app in all_apps:
            ret.append(app['package'])
        return ret
    
    @api.post("/uninstall")
    def uninstall(self):
        app_name = self['app_name']
        if app_name:
            from irails._utils import  enable_app
            from irails._loader import _unload_app 
            from irails.core import check_db_migrate
            if enable_app(app_name,False): 
                if _unload_app(application=application,app_name=app_name):
                    check_db_migrate()
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
                    n=_load_app(app_dir,app_name,app['manifest'],application)

                    if n and app_name in application.apps:
                        application.apps[app_name]['manifest'] = app['manifest']
                        _register_controllers()
                        mount_app_statics(application,app_name,debug)
                        check_db_migrate()
                        enable_app(app_name)
                        return 'OK'
        return 'Failed'
    
    @api.get("/get_configs")
    def get_configs(self):
        """
        :nav false
        """
        from irails.config import YamlConfig,ROOT_PATH
        import os
         
        domain = self.params('domain')
        
        configs = YamlConfig(os.path.join(ROOT_PATH, "configs"),merge_by_group=True)
        configs.config['general']['app']['all_apps'] = self.get_all_app_names()
        if not domain:
            return configs.config
        elif domain in configs.config:
            return configs.config[domain]
        else:
            return {}

    @api.post("/save_configs")
    def save_configs(self):
        from irails._utils import write_data_to_yaml
        from irails.config import ROOT_PATH
        import os
        domain = self.params("domain")
        data = self.params("data")
        if domain and data:
            file_path = os.path.join(ROOT_PATH,"configs",domain+".yaml")
            data_to_write = data #if  domain=='general' else {domain: data}
            if write_data_to_yaml(file_path,data_to_write,True):
                return 'OK'
            else:
                return "Failed"
        else:
            return 'Empty'