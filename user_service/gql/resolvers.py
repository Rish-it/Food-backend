import strawberry
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from user_service.services import OrderService, RestaurantService
from user_service.schemas import OrderCreate
from .types import (
    Order, Restaurant, OrderConnection,
    OrderInput, PaginationInput
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
        order_items=[
            {
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }
            for item in order_data.order_items
        ]
    )
def convert_restaurant_to_graphql(restaurant_data):
    """Convert Pydantic restaurant model to GraphQL Restaurant type"""
    return Restaurant(
        id=restaurant_data.id,
        name=restaurant_data.name,
        cuisine_type=restaurant_data.cuisine_type,
        address=restaurant_data.address,
        is_online=restaurant_data.is_online,
        operation_hours=restaurant_data.operation_hours,
        menu_items=[
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "is_available": item.is_available,
                "image_url": item.image_url
            }
            for item in restaurant_data.menu_items
        ]
    )
@strawberry.type
class Query:
    @strawberry.field
    async def restaurants(self, info) -> List[Restaurant]:
        """Get all available restaurants"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                restaurants = await service.get_online_restaurants()
                return [convert_restaurant_to_graphql(r) for r in restaurants]
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def restaurant(self, info, restaurant_id: UUID) -> Optional[Restaurant]:
        """Get restaurant by ID with menu"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                restaurant = await service.get_restaurant_with_menu(restaurant_id)
                return convert_restaurant_to_graphql(restaurant) if restaurant else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def order(self, info, order_id: UUID, user_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.get_order_by_id(order_id)
                
                if not order or order.user_id != user_id:
                    return None
                    
                return convert_order_to_graphql(order)
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def user_orders(
        self, 
        info, 
        user_id: UUID, 
        pagination: Optional[PaginationInput] = None
    ) -> OrderConnection:
        """Get user orders with pagination"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)  # Cap at 100
                
                orders = await service.get_user_orders(user_id, limit + 1, offset)
                
                has_next_page = len(orders) > limit
                if has_next_page:
                    orders = orders[:limit]
                
                return OrderConnection(
                    items=[convert_order_to_graphql(order) for order in orders],
                    total_count=len(orders),
                    has_next_page=has_next_page
                )
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_order(
        self, 
        info, 
        user_id: UUID, 
        order_input: OrderInput
    ) -> Order:
        """Create a new order"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                # Convert GraphQL input to Pydantic model
                order_data = OrderCreate(
                    restaurant_id=order_input.restaurant_id,
                    delivery_address=order_input.delivery_address,
                    items=[
                        {
                            "menu_item_id": item.menu_item_id,
                            "quantity": item.quantity
                        }
                        for item in order_input.items
                    ],
                    special_instructions=order_input.special_instructions
                )
                
                order = await service.create_order(user_id, order_data)
                return convert_order_to_graphql(order)
            except ValueError as e:
                await db.rollback()
                raise Exception(str(e)) 