from typing import List
from irails import database
from irails._i18n import _
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship,validates
 
import hashlib,os
 

class User(database.UserBase, database.Base):
     
    

    
    roles:List['Role'] = []

    apikeys:List['ApiKey'] = []
    
    salt = Column(String(50),comment="salt")
    remark = Column(String(255),comment="description")

    filter_columns_in_manager = ['salt','password']
    @classmethod
    def _general_columns(self):
        return super()._general_columns()
    
    @classmethod
    def before_insert(self,mapper, connection, target:'User'):
        # 在对象将要被插入到数据库之前触发
        if target.age and target.age<18:
            # 中断插入操作
            raise Exception('age must > 18')
        if target.username and not target.fullname:
            target.fullname = target.username
        if not target.domain:
            target.domain='system'
            
        if not target.password:
            password = target.username
        else:
            password = target.password
        salt = self.generate_salt()
        password = hashlib.sha256(password.encode('utf-8')+salt.encode("utf-8")).hexdigest()
        target.password=password
        target.salt = salt
    @classmethod
    def check_password(self,target:'User',password):
         
        salt = target.salt
        password = hashlib.sha256(password.encode('utf-8')+salt.encode("utf-8")).hexdigest()
        return password == target.password
    
    @classmethod
    def generate_salt(self)      : 
        return os.urandom(16).hex()
    
    def __repr__(self) -> str:
        name = _(self.username)
        return f"User(id={self.id!r}, name={name})"

class Role(database.Base):
    __tablename__ = f"roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users:List['User'] = []
    def on_change_name(target, value, oldvalue, initiator):
        print("Role:on_change_name" )
        return value 
class ApiKey(database.Base):
    __tablename__ = f"apikeys"
    id = Column(Integer,primary_key=True)
    name = Column(String(50),nullable=False)
    key = Column(String(255),nullable=False,unique=True)
    user:'User' = None

database.Schemes.M2O(ApiKey,User)

database.Schemes.M2M(User,Role)
database.Schemes.TIMESTAMPS(User,Role)
database.Schemes.SOFT_DELETE(User,Role)