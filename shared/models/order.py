from sqlalchemy import Column, String, JSON, DECIMAL, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.models.base import BaseModel


class Order(BaseModel):
    
    
    __tablename__="orders"
    __table_args__={'schema': 'orders'}
    
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    delivery_agent_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status= Column(String(50), default='pending', index=True)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    delivery_address=Column(JSON, nullable=False)
    special_instructions = Column(String)
    placed_at= Column(DateTime(timezone=True), server_default=func.now())
    accepted_at= Column(DateTime(timezone=True))
    delivered_at= Column(DateTime(timezone=True))
    
    
    
    #Relationship
    order_items= relationship("OrderItem", back_populates="order")
    rating = relationship("Rating", back_populates="order", uselist=False)


class OrderItem(BaseModel):
    __tablename__="order_items"
    __table_args__={'schema':'orders'}
    
    
    order_id= Column(UUID(as_uuid=True), ForeignKey('orders.orders.id'),nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10,2), nullable=False)
    
    order = relationship("Order", back_populates="order_items")
    
    
    
class Rating(BaseModel):
    __tablename__ = "ratings"
    __table_args__ = {'schema': 'orders'}
    
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.orders.id'), nullable=False, unique=True)
    user_id=Column(UUID(as_uuid=True), nullable=False)
    restaurant_rating = Column(Integer)  # 1-5 scale
    delivery_rating = Column(Integer)    # 1-5 scale
    restaurant_review = Column(String)
    delivery_review = Column(String)
    
    
    
    order= relationship("Order", back_populates="rating")
    
    
    
    
    
    