from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum
class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    
class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity:   int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v<=0:
            raise ValueError('Quantity must be greater') 
        return v 

class OrderItemResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    restaurant_id: UUID
    delivery_address: Dict[str, Any]
    items: List[OrderItemCreate]
    special_instructions: Optional[str] = None
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    delivery_agent_id: Optional[UUID]
    status: OrderStatus
    total_amount: Decimal
    delivery_address: Dict[str, Any]
    special_instructions: Optional[str]
    placed_at: datetime
    accepted_at: Optional[datetime]
    delivered_at: Optional[datetime]
    order_items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    restaurant_rating: Optional[int] = None
    delivery_rating: Optional[int] = None
    restaurant_review: Optional[str] = None
    delivery_review: Optional[str] = None
    
    @validator('restaurant_rating', 'delivery_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class RatingResponse(BaseModel):
    id: UUID
    order_id: UUID
    user_id: UUID
    restaurant_rating: Optional[int]
    delivery_rating: Optional[int]
    restaurant_review: Optional[str]
    delivery_review: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Restaurant schemas for user service
class MenuItemResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    is_available: bool
    image_url: Optional[str]
    
    class Config:
        from_attributes = True

class RestaurantResponse(BaseModel):
    id: UUID
    name: str
    cuisine_type: str
    address: Dict[str, Any]
    is_online: bool
    operation_hours: Optional[Dict[str, Any]]
    menu_items: List[MenuItemResponse] = []
    
    class Config:
        from_attributes = True
