# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
 
 
@application.on_event("startup")
def startup(): 
    #p, admin, domain1, data1, read 
    application.policy('admin','system','/sys_admin/*', '(GET)|(POST)', authorize=True) 
     
    #g, alice, admin, domain1 
    application.grouping('bruce','admin','system', authorize=True)

@route(path='/{controller}',auth='user',default='index')
class SysAdminController(BaseController): 
    
    @api.get('/index')
    def index(self):
        return self.view()                

    @api.get('/current_user')
    def current_user(self):
        import copy
        user = copy.copy(self.request.user)
        assert not user is self.request.user
        del user.token
        del user.payload
        return user