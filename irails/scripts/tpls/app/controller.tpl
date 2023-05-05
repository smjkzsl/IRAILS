# -*- coding: utf-8 -*- 
from irails import api_router,api,Request,Response,BaseController,application 
 
@api_router(path='/{controller}',auth='none')
class {{ctrl_name}}Controller(BaseController): 
    {{actions}}
     
    