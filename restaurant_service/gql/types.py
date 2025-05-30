import strawberry
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum
@strawberry.enum
class OrderStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
@strawberry.type
class Restaurant:
    id: UUID
    name: str
    email: str
    phone: str
    address: strawberry.scalars.JSON
    cuisine_type: str
    is_online: bool
    operation_hours: Optional[strawberry.scalars.JSON]
    created_at: datetime
@strawberry.type
class MenuItem:
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    is_available: bool
    image_url: Optional[str]
    created_at: datetime
@strawberry.type
class Order:
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    delivery_agent_id: Optional[UUID]
    status: OrderStatus
    total_amount: Decimal
    delivery_address: strawberry.scalars.JSON
    special_instructions: Optional[str]
    placed_at: datetime
    accepted_at: Optional[datetime]
    delivered_at: Optional[datetime]
    estimated_prep_time: Optional[int]
@strawberry.input
class RestaurantInput:
    name: str
    email: str
    phone: str
    address: strawberry.scalars.JSON
    cuisine_type: str
    operation_hours: Optional[strawberry.scalars.JSON] = None
@strawberry.input
class RestaurantUpdateInput:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[strawberry.scalars.JSON] = None
    cuisine_type: Optional[str] = None
    operation_hours: Optional[strawberry.scalars.JSON] = None
@strawberry.input
class MenuItemInput:
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    is_available: bool = True
    image_url: Optional[str] = None
@strawberry.input
class MenuItemUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
@strawberry.input
class OrderUpdateInput:
    status: Optional[OrderStatus] = None
    estimated_prep_time: Optional[int] = None
@strawberry.type
class RestaurantConnection:
    items: List[Restaurant]
    total_count: int
    has_next_page: bool
@strawberry.type
class MenuItemConnection:
    items: List[MenuItem]
    total_count: int
    has_next_page: bool
@strawberry.type
class OrderConnection:
    items: List[Order]
    total_count: int
    has_next_page: bool
@strawberry.input
class PaginationInput:
    limit: int = 50
    offset: int = 0
@strawberry.input
class MenuFilterInput:
    available_only: bool = False
    category: Optional[str] = None 