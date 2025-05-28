from sqlalchemy import Column, String, JSON, Boolean
from shared.models.base import BaseModel



class DeliveryAgent(BaseModel):
    __tablename__="delivery_agents"
    __table_args__={'schema':'delivery'}
    
    
    
    name=Column(String(255),  nullable=False)
    email=Column(String(255), nullable=False, unique=True)
    phone=Column(String(20),  nullable=False, unique=True,)
    is_available=Column(Boolean, default=True, index=True)
    current_location=Column(JSON)
    vehicle_type= Column(String(50))
    
    
    
    