# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 


@route(path='/{app}/{controller}',auth='user')
class AdminController(BaseController):  
    @api.get('/index')
    def index(self):
        '''
        :title 控制面板
        :nav true
        '''
        return self.view()                
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