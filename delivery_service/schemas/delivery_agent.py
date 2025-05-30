from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict
from datetime import datetime
import uuid

class LocationUpdate(BaseModel):
    """Schema for updating delivery agent location"""
    latitude: float
    longitude: float
    address: Optional[str] = None

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

class DeliveryAgentCreate(BaseModel):
    """Schema for creating a new delivery agent"""
    name: str
    email: EmailStr
    phone: str
    vehicle_type: str
    current_location: Optional[LocationUpdate] = None

    @validator('phone')
    def validate_phone(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v.strip()

    @validator('vehicle_type')
    def validate_vehicle_type(cls, v):
        allowed_types = ['bike', 'motorcycle', 'car', 'bicycle']
        if v.lower() not in allowed_types:
            raise ValueError(f'Vehicle type must be one of: {", ".join(allowed_types)}')
        return v.lower()

class DeliveryAgentUpdate(BaseModel):
    """Schema for updating delivery agent information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_available: Optional[bool] = None
    current_location: Optional[LocationUpdate] = None
    vehicle_type: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and (not v or len(v.strip()) < 10):
            raise ValueError('Phone number must be at least 10 digits')
        return v.strip() if v else v

    @validator('vehicle_type')
    def validate_vehicle_type(cls, v):
        if v is not None:
            allowed_types = ['bike', 'motorcycle', 'car', 'bicycle']
            if v.lower() not in allowed_types:
                raise ValueError(f'Vehicle type must be one of: {", ".join(allowed_types)}')
            return v.lower()
        return v

class DeliveryAgentResponse(BaseModel):
    """Schema for delivery agent response"""
    id: uuid.UUID
    name: str
    email: str
    phone: str
    is_available: bool
    current_location: Optional[Dict]
    vehicle_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 