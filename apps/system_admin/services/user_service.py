from irails.database import Service
from sqlalchemy import select
from typing import List
from system_admin.models import User

class UserService(Service):
    def get(self,id:int)->User:
        session = self.session()
        return session.get(User,id)
    def list(self):
        session = self.session()
        statement = select(User) 

        # list of ``User`` objects
        # objects = session.scalars(statement).all()
 
        # list of Row objects
        rows = session.execute(statement).all()
        return rows
    def add(self,user:User):
        session = self.session()
        session.add(user)
        session.commit()
        session.merge(user)
        return user
        
    def delete(self,user:User):
        with self.get_session() as session:
            session.delete(user)
        