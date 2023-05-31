from irails.database import Service
from sqlalchemy import select
from typing import List
from system_admin.models import User,Role

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
             
        except Exception as e:
            return False
         
        return user      