from sqlalchemy import Column, String, JSON
from shared.models.base import BaseModel

class User(BaseModel):
    __tablename__="users"
    __table_args__= {'schema': 'users'}


    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20),  unique=True, nullable=False, index=True)
    name =  Column(String(255), nullable=False)
    address = Column((JSON))

