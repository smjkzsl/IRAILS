
from irails import route,api,Request,Response,BaseController,application,WebSocket,WebSocketDisconnect,UploadFile,File

from typing import Any, Dict ,List
from pydantic import conlist
 

@application.on_event("startup")
def startup():
    
    #p, admin, domain1, data1, read
    application.policy('admin','system','/xml', 'GET', authorize=True)
    application.policy('admin','system','/sys_admin/*', 'GET', authorize=True)
    application.policy('admin','system','/chatgpt', 'GET', authorize=True)
    #g, alice, admin, domain1 
    application.grouping('bruce','admin','system', authorize=True)
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
    
    
    @api.get("/",auth='none' )
    def home(self,request:Request): 
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
        routers_map = application.routers_map
        routers = application.routes 
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


  