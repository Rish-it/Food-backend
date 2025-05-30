import strawberry
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import AsyncSessionLocal
from restaurant_service.services import RestaurantService, MenuService, OrderService
from restaurant_service.schemas import (
    RestaurantCreate, RestaurantUpdate,
    MenuItemCreate, MenuItemUpdate,
    OrderStatusUpdate
)
from .types import (
    Restaurant, MenuItem, Order,
    RestaurantConnection, MenuItemConnection, OrderConnection,
    RestaurantInput, RestaurantUpdateInput,
    MenuItemInput, MenuItemUpdateInput,
    OrderUpdateInput, PaginationInput, MenuFilterInput
)
def convert_restaurant_to_graphql(restaurant_data):
    """Convert Pydantic restaurant model to GraphQL Restaurant type"""
    return Restaurant(
        id=restaurant_data.id,
        name=restaurant_data.name,
        email=restaurant_data.email,
        phone=restaurant_data.phone,
        address=restaurant_data.address,
        cuisine_type=restaurant_data.cuisine_type,
        is_online=restaurant_data.is_online,
        operation_hours=restaurant_data.operation_hours,
        created_at=restaurant_data.created_at
    )
def convert_menu_item_to_graphql(menu_item_data):
    """Convert Pydantic menu item model to GraphQL MenuItem type"""
    return MenuItem(
        id=menu_item_data.id,
        restaurant_id=menu_item_data.restaurant_id,
        name=menu_item_data.name,
        description=menu_item_data.description,
        price=menu_item_data.price,
        category=menu_item_data.category,
        is_available=menu_item_data.is_available,
        image_url=menu_item_data.image_url,
        created_at=menu_item_data.created_at
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
        estimated_prep_time=getattr(order_data, 'estimated_prep_time', None)
    )
@strawberry.type
class Query:
    @strawberry.field
    async def restaurants(
        self, 
        info, 
        online_only: bool = False,
        pagination: Optional[PaginationInput] = None
    ) -> RestaurantConnection:
        """Get all restaurants with optional filtering"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)
                
                restaurants = await service.get_restaurants(online_only)
                
                # Apply pagination manually since the service doesn't support it
                total_count = len(restaurants)
                start = offset
                end = offset + limit
                
                paginated_restaurants = restaurants[start:end]
                has_next_page = end < total_count
                
                return RestaurantConnection(
                    items=[convert_restaurant_to_graphql(r) for r in paginated_restaurants],
                    total_count=total_count,
                    has_next_page=has_next_page
                )
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def restaurant(self, info, restaurant_id: UUID) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                restaurant = await service.get_restaurant_by_id(restaurant_id)
                return convert_restaurant_to_graphql(restaurant) if restaurant else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def menu_items(
        self, 
        info, 
        restaurant_id: UUID,
        filters: Optional[MenuFilterInput] = None,
        pagination: Optional[PaginationInput] = None
    ) -> MenuItemConnection:
        """Get menu items for a restaurant"""
        async with AsyncSessionLocal() as db:
            try:
                service = MenuService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)
                
                available_only = filters.available_only if filters else False
                category = filters.category if filters else None
                
                menu_items = await service.get_restaurant_menu_items(
                    restaurant_id, available_only, category, limit + 1, offset
                )
                
                has_next_page = len(menu_items) > limit
                if has_next_page:
                    menu_items = menu_items[:limit]
                
                return MenuItemConnection(
                    items=[convert_menu_item_to_graphql(item) for item in menu_items],
                    total_count=len(menu_items),
                    has_next_page=has_next_page
                )
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def menu_item(self, info, menu_item_id: UUID) -> Optional[MenuItem]:
        """Get menu item by ID"""
        async with AsyncSessionLocal() as db:
            try:
                service = MenuService(db)
                menu_item = await service.get_menu_item_by_id(menu_item_id)
                return convert_menu_item_to_graphql(menu_item) if menu_item else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.field
    async def restaurant_orders(
        self, 
        info, 
        restaurant_id: UUID,
        status_filter: Optional[str] = None,
        pagination: Optional[PaginationInput] = None
    ) -> OrderConnection:
        """Get orders for a restaurant"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                limit = pagination.limit if pagination else 50
                offset = pagination.offset if pagination else 0
                limit = min(limit, 100)
                
                if status_filter == "pending":
                    orders = await service.get_pending_orders(restaurant_id, limit + 1, offset)
                elif status_filter == "active":
                    orders = await service.get_active_orders(restaurant_id, limit + 1, offset)
                else:
                    orders = await service.get_restaurant_orders(restaurant_id, limit + 1, offset)
                
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

    @strawberry.field
    async def order(self, info, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.get_order_by_id(order_id)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_restaurant(
        self, 
        info, 
        restaurant_input: RestaurantInput
    ) -> Restaurant:
        """Create a new restaurant"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                
                restaurant_data = RestaurantCreate(
                    name=restaurant_input.name,
                    email=restaurant_input.email,
                    phone=restaurant_input.phone,
                    address=restaurant_input.address,
                    cuisine_type=restaurant_input.cuisine_type,
                    operation_hours=restaurant_input.operation_hours
                )
                
                restaurant = await service.create_restaurant(restaurant_data)
                return convert_restaurant_to_graphql(restaurant)
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_restaurant(
        self, 
        info, 
        restaurant_id: UUID,
        restaurant_input: RestaurantUpdateInput
    ) -> Optional[Restaurant]:
        """Update a restaurant"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                
                update_data = {}
                if restaurant_input.name is not None:
                    update_data['name'] = restaurant_input.name
                if restaurant_input.email is not None:
                    update_data['email'] = restaurant_input.email
                if restaurant_input.phone is not None:
                    update_data['phone'] = restaurant_input.phone
                if restaurant_input.address is not None:
                    update_data['address'] = restaurant_input.address
                if restaurant_input.cuisine_type is not None:
                    update_data['cuisine_type'] = restaurant_input.cuisine_type
                if restaurant_input.operation_hours is not None:
                    update_data['operation_hours'] = restaurant_input.operation_hours
                    
                restaurant_update = RestaurantUpdate(**update_data)
                restaurant = await service.update_restaurant(restaurant_id, restaurant_update)
                return convert_restaurant_to_graphql(restaurant) if restaurant else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_restaurant_status(
        self, 
        info, 
        restaurant_id: UUID,
        is_online: bool
    ) -> Optional[Restaurant]:
        """Update restaurant online status"""
        async with AsyncSessionLocal() as db:
            try:
                service = RestaurantService(db)
                restaurant = await service.update_restaurant_status(restaurant_id, is_online)
                return convert_restaurant_to_graphql(restaurant) if restaurant else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def create_menu_item(
        self, 
        info, 
        restaurant_id: UUID,
        menu_item_input: MenuItemInput
    ) -> MenuItem:
        """Create a new menu item"""
        async with AsyncSessionLocal() as db:
            try:
                service = MenuService(db)
                
                menu_item_data = MenuItemCreate(
                    name=menu_item_input.name,
                    description=menu_item_input.description,
                    price=menu_item_input.price,
                    category=menu_item_input.category,
                    is_available=menu_item_input.is_available,
                    image_url=menu_item_input.image_url
                )
                
                menu_item = await service.create_menu_item(restaurant_id, menu_item_data)
                return convert_menu_item_to_graphql(menu_item)
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_menu_item(
        self, 
        info, 
        menu_item_id: UUID,
        menu_item_input: MenuItemUpdateInput
    ) -> Optional[MenuItem]:
        """Update a menu item"""
        async with AsyncSessionLocal() as db:
            try:
                service = MenuService(db)
                
                update_data = {}
                if menu_item_input.name is not None:
                    update_data['name'] = menu_item_input.name
                if menu_item_input.description is not None:
                    update_data['description'] = menu_item_input.description
                if menu_item_input.price is not None:
                    update_data['price'] = menu_item_input.price
                if menu_item_input.category is not None:
                    update_data['category'] = menu_item_input.category
                if menu_item_input.is_available is not None:
                    update_data['is_available'] = menu_item_input.is_available
                if menu_item_input.image_url is not None:
                    update_data['image_url'] = menu_item_input.image_url
                    
                menu_item_update = MenuItemUpdate(**update_data)
                menu_item = await service.update_menu_item(menu_item_id, menu_item_update)
                return convert_menu_item_to_graphql(menu_item) if menu_item else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_menu_item_availability(
        self, 
        info, 
        menu_item_id: UUID,
        is_available: bool
    ) -> Optional[MenuItem]:
        """Update menu item availability"""
        async with AsyncSessionLocal() as db:
            try:
                service = MenuService(db)
                menu_item = await service.update_menu_item_availability(menu_item_id, is_available)
                return convert_menu_item_to_graphql(menu_item) if menu_item else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def accept_order(
        self, 
        info, 
        order_id: UUID,
        restaurant_id: UUID,
        estimated_prep_time: Optional[int] = None
    ) -> Optional[Order]:
        """Accept an order"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.accept_order(order_id, restaurant_id, estimated_prep_time)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def reject_order(
        self, 
        info, 
        order_id: UUID,
        restaurant_id: UUID,
        reason: Optional[str] = None
    ) -> Optional[Order]:
        """Reject an order"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.reject_order(order_id, restaurant_id, reason)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def update_order_status(
        self, 
        info, 
        order_id: UUID,
        restaurant_id: UUID,
        order_input: OrderUpdateInput
    ) -> Optional[Order]:
        """Update order status"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                
                status_update = OrderStatusUpdate(
                    status=order_input.status,
                    estimated_prep_time=order_input.estimated_prep_time
                )
                
                order = await service.update_order_status(order_id, restaurant_id, status_update)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e))

    @strawberry.mutation
    async def mark_order_ready(
        self, 
        info, 
        order_id: UUID,
        restaurant_id: UUID
    ) -> Optional[Order]:
        """Mark order as ready for pickup"""
        async with AsyncSessionLocal() as db:
            try:
                service = OrderService(db)
                order = await service.mark_order_ready(order_id, restaurant_id)
                return convert_order_to_graphql(order) if order else None
            except Exception as e:
                await db.rollback()
                raise Exception(str(e)) 