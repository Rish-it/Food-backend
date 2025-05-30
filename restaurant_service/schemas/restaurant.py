from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, List
from decimal import Decimal
from datetime import datetime
import uuid

class OperationHours(BaseModel):
    """Schema for restaurant operation hours"""
    monday: Optional[Dict[str, str]] = None
    tuesday: Optional[Dict[str, str]] = None
    wednesday: Optional[Dict[str, str]] = None
    thursday: Optional[Dict[str, str]] = None
    friday: Optional[Dict[str, str]] = None
    saturday: Optional[Dict[str, str]] = None
    sunday: Optional[Dict[str, str]] = None

class RestaurantCreate(BaseModel):
    """Schema for creating a new restaurant"""
    name: str
    email: EmailStr
    phone: str
    address: Dict
    cuisine_type: Optional[str] = None
    operation_hours: Optional[OperationHours] = None

    @validator('phone')
    def validate_phone(cls, v):
        # Basic phone validation
        if not v or len(v.strip()) < 10:
            raise ValueError('Phone number must be at least 10 digits')
        return v.strip()

class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant information"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[Dict] = None
    cuisine_type: Optional[str] = None
    is_online: Optional[bool] = None
    operation_hours: Optional[OperationHours] = None

class MenuItemResponse(BaseModel):
    """Schema for menu item response"""
    id: uuid.UUID
    restaurant_id: uuid.UUID
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    is_available: bool
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RestaurantResponse(BaseModel):
    """Schema for restaurant response"""
    id: uuid.UUID
    name: str
    email: str
    phone: str
    address: Dict
    cuisine_type: Optional[str]
    is_online: bool
    operation_hours: Optional[Dict]
    created_at: datetime
    updated_at: datetime
    menu_items: List[MenuItemResponse] = []

    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    """Schema for creating a new menu item"""
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    image_url: Optional[str] = None

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class MenuItemUpdate(BaseModel):
    """Schema for updating menu item"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v 