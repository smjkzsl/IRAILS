# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 
@route(path='/{controller}',auth='none')
class {{ctrl_name}}Controller(BaseController): 
    {{actions}}
     
    