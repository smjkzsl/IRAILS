from sqlalchemy.orm import Session
from sqlalchemy import select
from irails.database import engine,Service
from app.models import  *

class UserService(Service):
    @classmethod
    def add_user(cls,user:SysUser):
        with Session(engine) as session:
            session.add_all([user])
            session.commit()
    @classmethod
    def get_user(cls,uid):
        session = Session(engine) 
        if isinstance(uid,str):
            stmt = select(SysUser).where(SysUser.NickName==uid) 
        elif isinstance(uid,int):
            stmt = select(SysUser).where(SysUser.Id==uid) 
        user = session.scalars(stmt).one()
        return user
    pass
 