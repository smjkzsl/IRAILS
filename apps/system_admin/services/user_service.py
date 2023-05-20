from irails.database import Service
from sqlalchemy import select
from typing import List
from system_admin.models import User,Role

class UserService(Service):
    def get_user(self,id:int)->User: 
        return self.get(User,id)
    def list_user(self,**kwargs): 
        return self.list(User,**kwargs)
    def add_user(self,**kwargs):
        return self.add(User,**kwargs) 
    def delete_user(self,**kwargs):
        return self.delete(User,**kwargs)
        