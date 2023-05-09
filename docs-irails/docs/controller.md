 
## Controller

    The controller is a web application entry point, 
    a MVC applications must input requests into the controller for processing

    Commonly used must be imported:

        from irails import route,api,Request,Response,BaseController,application

### defines

        @route(path='/{controller}',auth='none')
        class ExampleController(BaseController):
            pass
        
* controller class must inherit `BaseController`
* controller must use `@route` decorator

    -  #### route  
        @route(path:str="", version:str="",**allargs) 

        The parameter path specifies the URL format, such as `app/{controller}/{version}`, which will be prefixed with `app/home/v1.0` as the route. Actions within the controller will be connected to this route, as defined by the controller
        Home action, the URL address of home is `/app/home/v1.0/home`, and version specifies the version information. If this parameter is provided, the path parameter will automatically carry the `{controller}` flag to define this route. For more information on auth, please refer to the authentication system.

    -  #### define a root URL 
       @route() #use empty params list to 

       
            @route()
            class HomeController(BaseController)
                @api.get("/")
                def home(self):
                    return self.view()
         
        it's will route to home method of the url '/'

### Actions
*   Defining an action is like defining a class instance method, 
    but it must use @ API decorators such as `@api.get`, `@api.post`, etc

    - #### @api decorator
        `@api.get`
        Use http method `GET` to define a route

        `@api.post`
        Use http method `POST` to define a route

        `@api.head`   ditto... but method is `HEAD`

        `@api.put`    ditto... but method is `PUT`

        `@api.delete` ditoo... but method is `DELETE`

        `@api.patch` ditoo... but method is `PATCH`

        `@api.trace`  ditoo... but method is `TRACE`

        `@api.options`  ditoo... but method is `OPTIONS`

        `@api.websocket`  define a websocket route. Example:

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

        `@api.http` ditoo... but it's provide param `methods`is a list like `['GET','POST']`

        with param `auth` ,also see the authentication system 


### Builtin supports of controller
     

* 
        self.request #the request object  
            self.request['url'] #the client request URL object
            self.request.headers['accept-languages'] 
* 
        self.session #the session object Dict
            self.session['key1'] = "K1" #set a session value
            v = self.session['key1'] #get a session value
            del self.session['key1'] #delete a session
* 
        self.cookies #the cookies object Dict
            self.cookies.get('a',1)
            self.cookies['a'] = self.cookies['a'] + 1
            del self.cookies['a']
* 
        self.get_param #get request param from any where
            self.get_param("username") #any use form'url query'post value
            self['password'] #same to self.get_param("password")
* 
        self.view #the Jinja2 Templace response 
            return self.view() #no param is render the default html file localed on `views/{controller_name}/{action_name}.html`
            """params: content:str="",view_path:str="", format:str="html", context: dict={},local2context:bool=True,**kwargs"""
            return self.view("Hello world") #just return `hello world` and status code is 200

            any value return on actions

                     return {"foo":"bar"} 
                     return "HEELO" 

            it  will convert Response object automatic

* 
        await self._save_upload_file(self,file:File) 

*       
        self._verity_successed(self,user,msg="User authentication successed!",redirect='/')


                also see the authentication system

* 
        self._verity_error(self,msg="User authentication failed!")


                also see the authentication system

* 
        self._user_logout(self,msg="You are successed logout!",redirect='/')


                also see the authentication system

* 
        self.redirect(self,url ,statu_code=StateCodes.HTTP_303_SEE_OTHER) 

* 
        self.flash


                Flash inspiration comes from the ROR, which is saved in the session. When its value is set, 
                it will be cleared when the next request is completed, so it is generally used to save one-time notifications,
                such as login success notifications
                
                self.flash = "you are success logined!"

* 
        self.log(msg:str)
        print log infomation to console or log file.
        for more infomation for log,see config.log

* 
        self._(text:str)
        Multilingual translation