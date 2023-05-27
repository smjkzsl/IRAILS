# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
from system_admin.services import UserService

@application.on_event("startup")
def startup(): 
    application.public_auth_url = '/system_admin/user/login'
    application.user_auth_url = '/system_admin/user/login'

@route("/{app}/{controller}",auth='user')
class UserController(BaseController):
    @api.get("/current_user")
    def current(self):
        import copy
        user = copy.copy(self.request.user)
        assert not user is self.request.user
        del user.token
        del user.payload
        return user
    @api.get("/login",auth="none" )
    def login(self):
        """:title 登陆"""  
        redirect = self.get_param('redirect') if self.get_param('redirect') else '/' 
        return self.view() 
    @api.post("/verity_user",auth="none")
    async def verity_user(self):  
        username = self['username']
        password = self['password']
        redirect = self['redirect']
        if username and password:
            service = UserService()
            user = service.verity(username=username,password=password)
            if user:
                userobj = application.new_user(user=user)
                userobj.domain = "system"
                return self._verity_successed(user = userobj,redirect= redirect)
            else:
                return self._verity_error() 
        return self._verity_error()
    
    @api.get("/logout")
    def logout(self):
        '''
        :title 注销
        '''
        return self._user_logout()