from typing import List
from irails import database
from irails._i18n import _
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship,validates
 

 

class User(database.Base):
    __tablename__ = f"{database.table_prefix}users"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50))

    fullname: Mapped[str] = mapped_column(String(50))

    age: Mapped[str] = mapped_column(Integer())
    roles:List['Role'] = []

    password = Column(String(50),comment="Password")
    remark = Column(String(255),comment="description")

    @staticmethod
    def before_insert(mapper, connection, target:'User'):
        # 在对象将要被插入到数据库之前触发
        if target.age<18:
            # 中断插入操作
            raise Exception('age must > 18')
             
        
    def __repr__(self) -> str:
        name = _(self.name)
        return f"User(id={self.id!r}, name={name})"

class Role(database.Base):
    __tablename__ = f"{database.table_prefix}roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users:List['User'] = []

database.Relations.M2M(User,Role)