from typing import List
from irails import database
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
 

 

class User(database.Base):
    __tablename__ = f"{database.table_prefix}users"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50))

    fullname: Mapped[str] = mapped_column(String(50))

    age: Mapped[str] = mapped_column(Integer())
    roles:List['Role'] = []

    password = Column(String(50),comment="Password")
    remark = Column(String(255),comment="description")
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"

class Role(database.Base):
    __tablename__ = f"{database.table_prefix}roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    users:List['User'] = []

database.Relations.M2M(User,Role)