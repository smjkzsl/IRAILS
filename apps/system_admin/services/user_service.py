from irails.database import Service
from sqlalchemy import select
from typing import List
from irails.apps.system_admin.models import User,Role,ApiKey
# from system_admin.models import User,Role,ApiKey

class UserService(Service):
    @classmethod
    def verity(self,username,password):
        try:
            user:User = self.query_user(username=username)
            if user and user.check_password(user,password):
                return user
            else:
                return False
        except Exception as e:
            return False
    @classmethod
    def query_user(self,username: str): 
        try:
            user:User = self.query(User,User.username==username).one()
            return user       
        except Exception as e:
            return False
         
        
    @classmethod
    def get_user_by_api_key(self,api_key:str):
        try:
            obj:ApiKey = Service.query(ApiKey,key=api_key).one()
            return obj.user
        except Exception as e:
            return None
        