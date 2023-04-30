from irails import controller,api_router,api,BaseController

@api_router(version="v1.0",path="/app1")
class Test1Controller(BaseController):
    
    @api.get('/home')#/app1/test1/v1.0/home
    def home(self):
        '''
        :title VUE3 PAGE
        '''
        return self.view()
    