# irails
A mvc framework used FastApi
Simple and elegant use of FastApi in MVC mode

[Demo](https://irails.2rails.cn/) 

### deploy one click on vercel:
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fsmjkzsl%irails&project-name=irails&repository-name=irails)

## usage:
### install:
```sh
pip install irails
```
### generate a project named `myproject` in current directory
```bash
irails project -d myproject
```
```bash
cd myproject 
```
now the project like this:
```
+---apps
+---configs
+---data
+---public
+---uploads 
```

### generate app
```bash
irails app 
[enter apps directory]
[enter app name like 'admin']
```
will generate an app in apps
### run project
```bash
irails run

    Started server process 
    Waiting for application startup.
    Application startup complete.
    Uvicorn running on  http://0.0.0.0:8000  (Press CTRL+C to quit)
```
open browser nav to http://127.0.0.1:8000 will see the web site

controller:
```python

from irails import api_router,api,Request,Response,BaseController,application,WebSocket,WebSocketDisconnect,UploadFile,File

from typing import Any, Dict ,List
from pydantic import conlist

application._public_auth_url = '/user/login'
application._user_auth_url = '/user/login'
 
@api_router(auth='public')
class TestController(BaseController): 
    @api.get("/user/login" )
    def login(self):
        """:title Login"""  
        redirect = self.get_param('redirect') if self.get_param('redirect') else '/' 
        return self.view() 
    @api.post("/test/verity_user",auth="none")
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
    
    @api.get("/user/logout")
    def logout(self):
        return self._user_logout()
    
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


 
 
websockets:Dict[str,WebSocket] = {}
import pusher

pusher_client = pusher.Pusher(
  app_id='1588311',
  key='3eb7cc894586d11b97de',
  secret='b1052d401c7d6542fc4f',
  cluster='ap3',
  ssl=True
)

@api_router(path="/{controller}")
class WSController(BaseController):  
    def __init__(self) -> None:
        super().__init__()
        
    @api.get("/" )
    def ws_home(self):
        """:title WebSocketDemo"""
        return self.view()

    @api.websocket("/chat/{client_id}")
    async def websocket_endpoint(self, websocket: WebSocket,client_id: int):
        await websocket.accept()
        websockets[client_id]=(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"You wrote: {data}" )
                for clientid in websockets:
                    if client_id!=clientid:
                        await websockets[clientid].send_text(f"Client #{client_id} says: {data}")
                 
        except WebSocketDisconnect:
            websockets.remove(websocket)
            for connection in websockets:
                await connection.send_text(f"Client #{client_id} left the chat")
             
```

home.html:

```html
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>FastApi MVC Framework</title>
    <link rel="stylesheet" href="home.css" />

</head>

<body>
    <header style="text-align:left;display: flex;">
        <h1>Python</h1>
        <h4>on FastApi</h4>

    </header>
    <nav>
        {% for item in routers_map %} {% if 'GET' in routers_map[item]['methods'] %} {% if routers_map[item]['auth']=='none' or request.session['user'] %}
        <a href="${routers_map[item]['path']}">${routers_map[item]['doc']
                and routers_map[item]['doc']['title'] or item}</a> {% endif %} {% endif %} {% endfor %}

        <a href="#">About</a>
        <a href="#">Contact</a> {% if request.session['user'] %}
        <a href="/user/logout"><b>${request.session['user']['username']}</b>
                Logout</a> {% endif %}
    </nav>
    <section>
        <h2>Welcome to my website</h2>
        <p>This is an example of a responsive design that works well on both desktop and mobile devices.</p>
        <p>here is the `text` variable in class method:${text}</p>
        <p style="color:red"><b>${flash}</b></p>
    </section>
    <footer>
        <p>&copy; 2023 My Website</p>
    </footer>
</body>

</html>
```
