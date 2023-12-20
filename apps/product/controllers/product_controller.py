# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 
@route(path='/{controller}',auth='none',default='index')
class ProductController(BaseController): 
    
    @api.get('/index')
    def index(self,p:str="",format='html'):
        view_path= "product/index"+"."+format
        return self.view(view_path=view_path,format=format)                

     
    