from irails import database
from sqlalchemy import Table,Column,ForeignKey,String,Integer
from sqlalchemy.orm import Mapped,mapped_column,relationship
 
class User(database.Base):
    __tablename__ = "users" 
    id: Mapped[int] = mapped_column(primary_key=True)
            
            
        
    name: Mapped[str] = mapped_column(String(50))
            
            
        
    fullname: Mapped[str] = mapped_column(String(50))
            
            
            
            
            
        
    age: Mapped[str] = mapped_column(Integer())
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"