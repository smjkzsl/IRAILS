from irails.database import Service
from sqlalchemy import select
from typing import List
from system_admin.models import User,Role

class UserService(Service):
    def verity(self,username,password):
        try:
            user:User = self.query(User,User.name==username).one()
            if user and user.check_password(user,password):
                return user
            else:
                return False
        except Exception as e:
            return False
          