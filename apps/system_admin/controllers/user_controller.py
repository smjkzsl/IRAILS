# -*- coding: utf-8 -*- 
from irails import route,api,Request,Response,BaseController,application 
from ..services import UserService
from urllib.parse import quote

@application.on_event("startup")
def startup(): 
    application.public_auth_url = '/system_admin/user/login'
    application.user_auth_url = '/system_admin/user/login'

@application.before_auth
def auth_api_key(request:Request,**kwargs):
    api_key = request.headers.get("api_key","")
    if not api_key: 
        return  None
    
    user = UserService.get_user_by_api_key(api_key)
    userobj = None
    if user: 
        userobj =  application.generate_auth_user(user=user)
    return  userobj

@route("/{app}/{controller}",auth='user')
class UserController(BaseController):
    @api.get("/current_user" )
    def current(self):
        '''
        :nav false
        '''
        import copy
        user = copy.copy(self.request.user)
        assert not user is self.request.user
        if hasattr(user,'token'):
            del user.token
        if hasattr(user,'payload'):
            del user.payload
        return user
    @api.get("/i18n_list",auth="none")
    def i18n_list(self):
        from irails._i18n import get_all
        rets = get_all()
        return rets
         

    @api.get("/api_keys")
    def api_keys(self):
        user = self.request.user
        apikeys = UserService.list_user_apikeys(user.id)
        return apikeys
    
    @api.http("/login",methods=['POST','GET'] ,auth="none" )
    def login(self):
        """:title 登陆"""  

        if self.request.method=='GET':
            redirect = self.params('redirect') if self.params('redirect') else '/' 
            redirect = quote(redirect)
            return self.view() 
    
        else:
            username = self['username']
            password = self['password']
            redirect = self['redirect']
            if username and password:
                service = UserService()
                user = service.verity(username=username,password=password)
                if user:
                    userobj =  application.generate_auth_user(user=user)
                    
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