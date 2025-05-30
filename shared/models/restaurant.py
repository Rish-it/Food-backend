from sqlalchemy import Column, String, JSON, Boolean, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from shared.models.base import BaseModel
class Restaurant(BaseModel):
    __tablename__ = "restaurants"
    __table_args__ = {'schema': 'restaurants'}
    
    name  = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address  = Column(JSON, nullable=False)
    cuisine_type  = Column(String(100))
    is_online  = Column(Boolean, default=False)
    operation_hours  = Column(JSON)
    
    #relationship to menu 
    menu_items = relationship("MenuItem", back_populates="restaurant")
    
    
    
class MenuItem(BaseModel):
    __tablename__= "menu_items"
    __table_args__= {'schema': 'restaurants'}
    
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey('restaurants.restaurants.id'), nullable=False)
    name =Column(String(255), nullable=False)
    description = Column(String)
    price= Column(DECIMAL(10, 2), nullable=False)
    category = Column(String(100))
    is_available = Column(Boolean, default=True)
    image_url = Column(String(500))
    
    
    #relationship 
    restaurant = relationship("Restaurant", back_populates="menu_items")
    
    
    
    
    
    
    
    
    
    
    
    
       
    
  
    