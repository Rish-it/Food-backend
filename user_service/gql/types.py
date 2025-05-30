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
class OrderItem:
    id: UUID
    menu_item_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
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
    order_items: List[OrderItem]
@strawberry.type
class MenuItem:
    id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    category: Optional[str]
    is_available: bool
    image_url: Optional[str]
@strawberry.type
class Restaurant:
    id: UUID
    name: str
    cuisine_type: str
    address: strawberry.scalars.JSON
    is_online: bool
    operation_hours: Optional[strawberry.scalars.JSON]
    menu_items: List[MenuItem]
@strawberry.input
class OrderItemInput:
    menu_item_id: UUID
    quantity: int
@strawberry.input
class OrderInput:
    restaurant_id: UUID
    delivery_address: strawberry.scalars.JSON
    items: List[OrderItemInput]
    special_instructions: Optional[str] = None
@strawberry.type
class OrderConnection:
    items: List[Order]
    total_count: int
    has_next_page: bool
@strawberry.input
class PaginationInput:
    limit: int = 50
    offset: int = 0 