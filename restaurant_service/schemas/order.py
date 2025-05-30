from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class OrderUpdateRequest(BaseModel):
    """Schema for updating order status from restaurant"""
    status: str  # 'accepted', 'rejected', 'preparing', 'ready_for_pickup'
    estimated_prep_time: Optional[int] = None  # in minutes

class OrderStatusUpdate(BaseModel):
    """Schema for order status update response"""
    order_id: uuid.UUID
    status: str
    updated_at: datetime
    estimated_prep_time: Optional[int] = None

class DeliveryAssignment(BaseModel):
    """Schema for delivery agent assignment"""
    order_id: uuid.UUID
    delivery_agent_id: uuid.UUID
    assigned_at: datetime

class OrderItemResponse(BaseModel):
    """Schema for order item in restaurant context"""
    id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class RestaurantOrderResponse(BaseModel):
    """Schema for order response in restaurant context"""
    id: uuid.UUID
    user_id: uuid.UUID
    restaurant_id: uuid.UUID
    delivery_agent_id: Optional[uuid.UUID]
    status: str
    total_amount: float
    delivery_address: dict
    special_instructions: Optional[str]
    placed_at: datetime
    accepted_at: Optional[datetime]
    delivered_at: Optional[datetime]
    order_items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True 