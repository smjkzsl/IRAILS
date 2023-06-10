# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 
@route(path='/{controller}',auth='none')
class ProductController(BaseController): 
    
    @api.get('/index')
    def index(self):
        return self.view()                

     
    