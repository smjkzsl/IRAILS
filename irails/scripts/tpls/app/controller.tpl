# -*- coding: utf-8 -*- 
from irails import api_router,api,Request,Response,BaseController,application,WebSocket,WebSocketDisconnect,UploadFile,File

from typing import Any, Dict ,List
from pydantic import conlist 

@api_router(path='/{controller}',auth='none')
class {{ctrl_name}}Controller(BaseController): 
    @api.get("/index")
    def index(self):
        """
        :title {{ctrl_name}}
        """
        return self.view()
    


    @api.get("/login" )
    def login(self):
        """:title Login"""  
        redirect = self.get_param('redirect') if self.get_param('redirect') else '/' 
        return self.view() 
    @api.post("/verity_user",auth="none")
    async def verity_user(self):  
        username = self['username']
        password = self['password']
        redirect = self['redirect']
        if username and password:
            #do veritied
            if username in ['bruce','alice'] and password:
                return self._verity_successed(username,redirect)
            else:
                return self._verity_error() 
        return self._verity_error()
    
    @api.get("/logout")
    def logout(self):
        return self._user_logout()
    
    @api.post("/upload")
    async def upload_test(self, files: List[UploadFile] = File(...) ): 
        p = {}
        for file in files:
            path,url = await self._save_upload_file(file)
            p[file.filename] = [path,url]
        return {"files":p} 
    
     
    