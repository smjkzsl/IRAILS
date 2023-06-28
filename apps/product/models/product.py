from irails import database
from sqlalchemy import Table,Column,ForeignKey,String,Integer
from sqlalchemy.orm import Mapped,mapped_column,relationship
 
class Product(database.Base):
    __tablename__ = "products" 
    
            
            
        
    id: Mapped[str] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(50),comment="name of product")