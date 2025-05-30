import strawberry
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum
@strawberry.enum
class VehicleType(Enum):
    BIKE = "bike"
    MOTORCYCLE = "motorcycle"
    CAR = "car"
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
class Location:
    latitude: float
    longitude: float
    address: Optional[str] = None
@strawberry.type
class DeliveryAgent:
    id: UUID
    name: str
    email: str
    phone: str
    vehicle_type: VehicleType
    is_available: bool
    current_location: Optional[Location]
    deliveries_completed: int
    average_rating: Optional[float]
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
    pickup_time: Optional[datetime]
@strawberry.type
class DeliveryAssignment:
    id: UUID
    order_id: UUID
    delivery_agent_id: UUID
    restaurant_id: UUID
    assigned_at: datetime
    pickup_time: Optional[datetime]
    delivery_time: Optional[datetime]
    status: str
@strawberry.input
class LocationInput:
    latitude: float
    longitude: float
    address: Optional[str] = None
@strawberry.input
class DeliveryAgentInput:
    name: str
    email: str
    phone: str
    vehicle_type: VehicleType
    current_location: Optional[LocationInput] = None
@strawberry.input
class DeliveryAgentUpdateInput:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    is_available: Optional[bool] = None
@strawberry.input
class AssignmentInput:
    order_id: UUID
    delivery_agent_id: UUID
    restaurant_id: UUID
@strawberry.input
class DeliveryStatusUpdateInput:
    status: Optional[str] = None
    location: Optional[LocationInput] = None
    notes: Optional[str] = None
@strawberry.type
class DeliveryAgentConnection:
    items: List[DeliveryAgent]
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