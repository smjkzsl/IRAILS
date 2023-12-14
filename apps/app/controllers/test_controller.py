
from irails import route,api,Request,Response,BaseController,application,WebSocket,WebSocketDisconnect,UploadFile,File

from typing import Any, Dict ,List
from pydantic import conlist
 


@route(auth='none')
class TestController(BaseController): 
    def __init__(self) -> None:
        
        super().__init__()
    
    
    @api.post("/test/upload")
    async def upload_test(self, files: List[UploadFile] = File(...) ): 
        p = {}
        for file in files:
            path,url = await self._save_upload_file(file)
            p[file.filename] = [path,url]
        return {"files":p} 
    
    @api.get('/react_home',auth='none')
    def react_home(self ):
        '''
        :title React Home
        '''
        return self.view()
    
    @api.get("/",auth='none' )
    async def home(self,request:Request): 
        '''
        :title Home
        '''
        c = self.session.get('home',1)
        c = c+1  
        self.cookies["a"] = c
        if c>10:
            del self.cookies["a"]
            c = 0
        self.session['home'] = c
        text = "Hello World! I'm in FastapiMvcFramework"
        router_map = {}
        for app_name in application.apps:
            if not app_name in router_map:
                router_map[app_name]={}
            router_map[app_name]['title'] = application.apps[app_name]['manifest']['title'] or app_name
            for func in application.apps[app_name]['route_map']:
                item = application.apps[app_name]['route_map'][func]
                if item['doc']:
                    if (not 'nav' in item['doc'] ) or ('nav' in item['doc'] and item['doc']['nav'].lower() != 'false'):

                        router_map[app_name][func] = application.apps[app_name]['route_map'][func]
                else:
                    router_map[app_name][func] = application.apps[app_name]['route_map'][func]
        app_name = application.title

        #访问其它模块中的控制器函数，如果是一个被@api装饰的函数 ,不能直接调用
        from irails.apps.system_admin.controllers.user_controller import UserController
        u = UserController(request=self.request,response=self.response)
        curuser =   u.current()
        try:
            curuser.send(None) #使用send函数
        except StopIteration   as e:
            aa =  e.value #从这里获取运行结果 
             
        return self.view( )



        return self.view()
    
    @api.get("/xml",auth='user')
    def get_legacy_data(self):
        """:title XML(only bruce)"""

        data = """<?xml version="1.0"?>
        <shampoo>
        <Header>
            Apply shampoo here.
        </Header>
        <Body>
            You'll have to use soap here.
        </Body>
        </shampoo>
        """
        return self.view(content=data,media_type="application/xml")
          
    @api.get("/chatgpt",auth="user")
    def chatgpt(self):
        """
        :title Chat(only alice)
        """
        return self.view()


  