#usage: `pytest` 

import requests
url = "http://localhost:8000"
headers = {"Authorization": "",'Accept':'application/json'}

def request(uri,method="GET",**args):
    _url = url+uri
    print(method + '  ' + _url)
    response = requests.request(method=method,url=_url,headers=headers,**args)
    return response

def test_root(): 
    response = request('/')
    assert response.status_code == 200
    assert response.text.find('Welcome to my website')>0

def test_user_login_page():
 
    response = request('/user/login')
    assert response.status_code == 200
    assert response.text.find('Password')>0

def test_get_item_not_found():
 
    response = request('/items/100')
    assert response.status_code == 404
    assert response.text.find('sorry')>0
def test_not_authenticated(): 
    response = request('/xml')
    assert response.status_code == 401
    assert response.json() == {"message": "401 UNAUTHORIZED!"}
def test_user_login():
    response = request('/test/verity_user','POST',data={'username':"bruce","password":'ppp'})
    assert response.status_code == 200
    json = response.json() 
    print(json)
    assert json['token']!=""
    headers['Authorization'] = "Bearer "+json['token']
def test_not_authenticated_by_authenticated(): 
    response = request('/xml')
    assert response.status_code == 200
    assert response.text.find("You'll have to use soap here")>0