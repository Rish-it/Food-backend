import strawberry
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from delivery_service.services import DeliveryAgentService, OrderService
from delivery_service.schemas import (
    DeliveryAgentCreate, DeliveryAgentUpdate,
    AssignmentRequest, DeliveryStatusUpdate
)
from .types import (
    DeliveryAgent, Order, DeliveryAssignment,
    DeliveryAgentConnection, OrderConnection,
    DeliveryAgentInput, DeliveryAgentUpdateInput,
    AssignmentInput, DeliveryStatusUpdateInput,
    PaginationInput, LocationInput, Location
)
def convert_location_to_graphql(location_data):
    """Convert location data to GraphQL Location type"""
    if not location_data:
        return None
    return Location(
        latitude=location_data.get('latitude'),
        longitude=location_data.get('longitude'),
        address=location_data.get('address')
    )
def convert_delivery_agent_to_graphql(agent_data):
    """Convert Pydantic delivery agent model to GraphQL DeliveryAgent type"""
    return DeliveryAgent(
        id=agent_data.id,
        name=agent_data.name,
        email=agent_data.email,
        phone=agent_data.phone,
        vehicle_type=agent_data.vehicle_type,
        is_available=agent_data.is_available,
        current_location=convert_location_to_graphql(agent_data.current_location),
        deliveries_completed=0,  # Default value since it's not in the response
        average_rating=None,  # Default value since it's not in the response
        created_at=agent_data.created_at
    )
def convert_order_to_graphql(order_data):
    """Convert Pydantic order model to GraphQL Order type"""
    return Order(
        id=order_data.id,
        user_id=order_data.user_id,
        restaurant_id=order_data.restaurant_id,
        delivery_agent_id=order_data.delivery_agent_id,
        status=order_data.status,
        total_amount=order_data.total_amount,
        delivery_address=order_data.delivery_address,
        special_instructions=order_data.special_instructions,
        placed_at=order_data.placed_at,
        accepted_at=order_data.accepted_at,
        delivered_at=order_data.delivered_at,
        pickup_time=getattr(order_data, 'pickup_time', None)
    )
@strawberry.type
class Query:
    @strawberry.field
    async def delivery_agents(
        self, 
        info, 
        available_only: bool = False,
        pagination: Optional[PaginationInput] = None
    ) -> DeliveryAgentConnection:
        """Get delivery agents with optional filtering"""
        async with AsyncSessionLocal() as db:
            try:
                service = DeliveryAgentService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)
                
                agents = await service.get_delivery_agents(available_only)
                
                # Apply pagination manually since the service doesn't support it
                total_count = len(agents)
                start = offset
                end = offset + limit
                
                paginated_agents = agents[start:end]
                has_next_page = end < total_count
                
                return DeliveryAgentConnection(
                    items=[convert_delivery_agent_to_graphql(agent) for agent in paginated_agents],
                    total_count=total_count,
                    has_next_page=has_next_page
                )
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def delivery_agent(self, info, agent_id: UUID) -> Optional[DeliveryAgent]:
        """Get delivery agent by ID"""
        async with AsyncSessionLocal() as db:
            try:
                service = DeliveryAgentService(db)
                agent = await service.get_delivery_agent_by_id(str(agent_id))
                return convert_delivery_agent_to_graphql(agent) if agent else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def agent_orders(
        self, 
        info, 
        agent_id: UUID,
        active_only: bool = False,
        pagination: Optional[PaginationInput] = None
    ) -> OrderConnection:
        """Get orders assigned to a delivery agent"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)
                
                orders = await service.get_agent_orders(str(agent_id))
                
                # Apply pagination manually
                total_count = len(orders)
                start = offset
                end = offset + limit
                
                paginated_orders = orders[start:end]
                has_next_page = end < total_count
                
                return OrderConnection(
                    items=[convert_order_to_graphql(order) for order in paginated_orders],
                    total_count=total_count,
                    has_next_page=has_next_page
                )
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_delivery_agent(
        self, 
        info, 
        agent_input: DeliveryAgentInput
    ) -> DeliveryAgent:
        """Create a new delivery agent"""
        async with AsyncSessionLocal() as db:
            try:
                service = DeliveryAgentService(db)
                
                location_data = None
                if agent_input.current_location:
                    location_data = {
                        "latitude": agent_input.current_location.latitude,
                        "longitude": agent_input.current_location.longitude,
                        "address": agent_input.current_location.address
                    }
                
                agent_data = DeliveryAgentCreate(
                    name=agent_input.name,
                    email=agent_input.email,
                    phone=agent_input.phone,
                    vehicle_type=agent_input.vehicle_type,
                    current_location=location_data
                )
                
                agent = await service.create_agent(agent_data)
                return convert_delivery_agent_to_graphql(agent)
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_delivery_agent(
        self, 
        info, 
        agent_id: UUID,
        agent_input: DeliveryAgentUpdateInput
    ) -> Optional[DeliveryAgent]:
        """Update a delivery agent"""
        async with AsyncSessionLocal() as db:
            try:
                service = DeliveryAgentService(db)
                
                update_data = {}
                if agent_input.name is not None:
                    update_data['name'] = agent_input.name
                if agent_input.email is not None:
                    update_data['email'] = agent_input.email
                if agent_input.phone is not None:
                    update_data['phone'] = agent_input.phone
                if agent_input.vehicle_type is not None:
                    update_data['vehicle_type'] = agent_input.vehicle_type
                if agent_input.is_available is not None:
                    update_data['is_available'] = agent_input.is_available
                    
                agent_update = DeliveryAgentUpdate(**update_data)
                agent = await service.update_agent(agent_id, agent_update)
                return convert_delivery_agent_to_graphql(agent) if agent else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_agent_location(
        self, 
        info, 
        agent_id: UUID,
        location: LocationInput
    ) -> Optional[DeliveryAgent]:
        """Update delivery agent location"""
        async with AsyncSessionLocal() as db:
            try:
                service = DeliveryAgentService(db)
                
                location_data = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address
                }
                
                agent = await service.update_agent_location(agent_id, location_data)
                return convert_delivery_agent_to_graphql(agent) if agent else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def assign_order(
        self, 
        info, 
        assignment_input: AssignmentInput
    ) -> bool:
        """Assign an order to a delivery agent"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                assignment_data = AssignmentRequest(
                    order_id=assignment_input.order_id,
                    delivery_agent_id=assignment_input.delivery_agent_id,
                    restaurant_id=assignment_input.restaurant_id
                )
                
                success = await service.receive_assignment(assignment_data)
                return success
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def mark_order_picked_up(
        self, 
        info, 
        order_id: UUID,
        agent_id: UUID
    ) -> Optional[Order]:
        """Mark order as picked up"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.mark_order_picked_up(order_id, agent_id)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def mark_order_delivered(
        self, 
        info, 
        order_id: UUID,
        agent_id: UUID
    ) -> Optional[Order]:
        """Mark order as delivered"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.mark_order_delivered(order_id, agent_id)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e)) 