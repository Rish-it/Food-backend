from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uuid

class DeliveryStatusUpdate(BaseModel):
    """Schema for updating delivery status"""
    status: str  # 'assigned', 'picked_up', 'on_the_way', 'delivered'
    location: Optional[Dict] = None
    notes: Optional[str] = None

class AssignmentRequest(BaseModel):
    """Schema for order assignment to delivery agent"""
    order_id: uuid.UUID
    delivery_agent_id: uuid.UUID
    assigned_at: datetime

class DeliveryOrderResponse(BaseModel):
    """Schema for order response in delivery context"""
    id: uuid.UUID
    user_id: uuid.UUID
    restaurant_id: uuid.UUID
    delivery_agent_id: Optional[uuid.UUID]
    status: str
    total_amount: float
    delivery_address: Dict
    special_instructions: Optional[str]
    placed_at: datetime
    accepted_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True

class DeliveryAssignmentResponse(BaseModel):
    """Schema for delivery assignment response"""
    id: uuid.UUID
    order_id: uuid.UUID
    agent_id: uuid.UUID
    status: str
    assigned_at: datetime
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]
    current_location: Optional[Dict]

class LocationTrackingUpdate(BaseModel):
    """Schema for location tracking updates"""
    delivery_agent_id: uuid.UUID
    order_id: uuid.UUID
    latitude: float
    longitude: float
    timestamp: datetime
    estimated_arrival: Optional[datetime] = None 