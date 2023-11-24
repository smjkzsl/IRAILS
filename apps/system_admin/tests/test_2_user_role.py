from typing import Any, Dict, Union
from irails.unit_test import *
from irails import application
from fastapi import status 

class TestUserRole(ControllerTest):
    def __init__(self, *args, **kwargv) -> None:
        super().__init__(*args, **kwargv)
        # database.Service.execute('delete from casbin_rule')

        self.headers={}
        self._token:str = ""    
            #p, admin, domain1, data1, read 
        application.policy('admin','system','/system_admin/admin/*', '(GET)|(POST)', authorize=True) 
        application.policy('admin','system','/system_admin/user/*', '(GET)|(POST)', authorize=True)  
        application.policy('user','system','/system_admin/user/*', '(GET)|(POST)', authorize=True)  
        application.policy('kefu','system','/system_admin/user/api_keys', '(GET)|(POST)', authorize=True)  
        application.policy('kefu','system','/chatgpt', '(GET)|(POST)', authorize=True)  
        #g, alice, admin, domain1 
        application.grouping('bruce','user','system', authorize=True)
        application.grouping('root','admin','system', authorize=True)
        application.grouping('alice','kefu','system', authorize=True)

    def _request(self,path:str,method:str="GET",data=None,ret_json=True,request_json=True)->Union[Dict,Any]:
        if request_json:
            accept = 'application/json'
        else:
            accept = '*/*'
        headers = dict(self.headers, Accept = accept )
        if self._token:
            headers.update({'Authorization': f"Bearer {self._token}"})
         
        response =  self.client.request(method=method,url=path,headers=headers,data=data)
        if ret_json:
            return response.json()
        else:
            return response
     
        
    def user_login(self,username='root',password=""):
        if not password:
            password=username
        data = {'username':username,'password':password}
        result = self._request("/system_admin/user/login",method="POST",data=data)
        self.assertEqual(result['status'],'success')
        self.assertTrue(result['token'])
        self._token = result['token']

    def access_right_user_root(self):
        result = self._request(path='/system_admin/admin/index',ret_json=False)
        self.assertEqual(result.status_code,200)
        result = self._request(path='/system_admin/user/current_user',ret_json=False)
        self.assertEqual(result.status_code,200)
        result = self._request(path='/xml',ret_json=False)
        self.assertEqual(result.status_code,200)
        result = self._request(path='/chatgpt',ret_json=False)
        self.assertEqual(result.status_code,200)
        
    def access_deny(self):
        self.user_login(username='alice')
        result = self._request(path='/system_admin/admin/index',ret_json=False)
        self.assertEqual(result.status_code,status.HTTP_403_FORBIDDEN)
        result = self._request(path='/xml',ret_json=False)
        self.assertEqual(result.status_code,status.HTTP_403_FORBIDDEN)
        self.user_login(username='bruce')
        application.grouping('bruce','admin','system',authorize=False)
        result = self._request(path='/chatgpt',ret_json=False)
        
        self.assertEqual(result.status_code,status.HTTP_403_FORBIDDEN)
        result = self._request(path='/xml',ret_json=False)
        self.assertEqual(result.status_code,status.HTTP_403_FORBIDDEN)
        
    def access_kefu_user(self):
        self.user_login(username='alice')
        result = self._request(path='/system_admin/admin/index',ret_json=False)
        self.assertEqual(result.status_code,403)

        result = self._request(path='/chatgpt',ret_json=False)
        self.assertEqual(result.status_code,200)

    def access_by_apikey(self):
        self.user_login(username='alice')
        apikeys = self._request('/system_admin/user/api_keys')
        self.assertGreater(len(apikeys),0)
        apikey = apikeys[0]['key']
        self._token = ""
        self.client.cookies.clear()
        self.headers.update({"api_key":apikey})
        result = self._request(path='/chatgpt',ret_json=False)
        self.assertEqual(result.status_code,200)
        
    def runTest(self):
        a=self._request(path="/xml",ret_json=False)
        self.assertEqual(a.status_code,status.HTTP_401_UNAUTHORIZED)
        self.user_login()
        self.access_right_user_root()
        self.access_deny()
        self.access_kefu_user()
        self.access_by_apikey()