# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 


@route(path='/{app}/{controller}',auth='user')
class AdminController(BaseController):  
    @api.get('/index')
    def index(self):
        return self.view()                
 