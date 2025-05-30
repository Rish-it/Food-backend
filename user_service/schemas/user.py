from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    phone: str
    name: str
    address: Optional[Dict[str, Any]] = None
    
    
    
class UserCreate(UserBase):
    @validator('phone')
    def validator_phone(cls, v):
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, +, -, and spaces')
        return v
    

class UserResponse(UserBase):
    id: UUID
    created_at:datetime
    updated_at:datetime
    
    
    class Config:
        from_attributes = True
