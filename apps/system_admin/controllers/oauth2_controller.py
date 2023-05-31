import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from irails import BaseController,api,application
from system_admin.services.oauth2_service import OAuth2Service, OAuth
from system_admin.services import UserService
from system_admin.models.oauth2 import *

oauth = OAuth(application)
@oauth.register(name='test')
def create_oauth_client():
    return {
        'client_id': 'client_id',
        'client_secret': 'client_secret',
        'redirect_uris': 'http://localhost:8000/callback',  # change this to your url
        'default_scopes': ['email'],
    }



oauth = OAuth(application)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class OAuth2ServerController(BaseController):

    
    @api.post("/token", response_model=OAuth2Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        username = form_data.username
        password = form_data.password
        user =UserService.verity(username,password)
        if not user  :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Here is where the complete OAuth2 Token Generation happens
        # You should replace this with your complete OAuth2 Token generation step
        token_data = {"access_token": "access_token_example", "token_type": "bearer"}
        return OAuth2Service.create_user_token(user.id, token_data)

    @api.get("/users/me")
    async def read_users_me(current_user: str = Depends(oauth2_scheme)):
        return {"username": current_user}
