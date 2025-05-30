from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from decimal import Decimal
import httpx
import logging
from uuid import UUID

from shared.models.order import Order, OrderItem, Rating
from shared.models.restaurant import MenuItem
from ..schemas import (
    OrderCreate, OrderResponse, RatingCreate, RatingResponse
)

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(self, user_id: UUID, order_data: OrderCreate) -> OrderResponse:
        """Create a new order"""
        try:
            # Validate menu items and calculate total
            total_amount = Decimal('0.00')
            order_items_data = []
            
            for item in order_data.items:
                # Fetch menu item details
                stmt = select(MenuItem).where(
                    MenuItem.id == item.menu_item_id,
                    MenuItem.is_available == True
                )
                result = await self.db.execute(stmt)
                menu_item = result.scalar_one_or_none()
                
                if not menu_item:
                    raise ValueError(f"Menu item {item.menu_item_id} not found or unavailable")
                
                # Verify the menu item belongs to the specified restaurant
                if menu_item.restaurant_id != order_data.restaurant_id:
                    raise ValueError(f"Menu item {item.menu_item_id} does not belong to restaurant {order_data.restaurant_id}")
                
                item_total = menu_item.price * item.quantity
                total_amount += item_total
                
                order_items_data.append({
                    'menu_item_id': item.menu_item_id,
                    'quantity': item.quantity,
                    'unit_price': menu_item.price,
                    'total_price': item_total
                })
            
            # Create the order
            db_order = Order(
                user_id=user_id,
                restaurant_id=order_data.restaurant_id,
                total_amount=total_amount,
                delivery_address=order_data.delivery_address,
                special_instructions=order_data.special_instructions,
                status='pending'
            )
            
            self.db.add(db_order)
            await self.db.flush()

            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=db_order.id,
                    **item_data
                )
                self.db.add(order_item)
            
            await self.db.commit()
            
            await self._notify_restaurant_service(db_order.id, order_data.restaurant_id)
            
            return await self.get_order_by_id(db_order.id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating order: {e}")
            raise
    
    async def get_order_by_id(self, order_id: UUID) -> Optional[OrderResponse]:
        """Get order by ID with all details"""
        try:
            stmt = (
                select(Order)
                .options(selectinload(Order.order_items))
                .where(Order.id == order_id)
            )
            
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                return None
                
            return OrderResponse.from_orm(order)
            
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    async def get_user_orders(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[OrderResponse]:
        """Get all orders for a user"""
        try:
            stmt = (
                select(Order)
                .options(selectinload(Order.order_items))
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.db.execute(stmt)
            orders = result.scalars().all()
            
            return [OrderResponse.from_orm(order) for order in orders]
            
        except Exception as e:
            logger.error(f"Error fetching user orders for {user_id}: {e}")
            raise
    
    async def create_rating(self, user_id: UUID, order_id: UUID, rating_data: RatingCreate) -> RatingResponse:
        """Create a rating for an order"""
        try:
            # Verify order exists and belongs to user
            stmt = select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.status == 'delivered'
            )
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                raise ValueError("Order not found, doesn't belong to user, or not delivered")
            
            # Check if rating already exists
            stmt = select(Rating).where(Rating.order_id == order_id)
            result = await self.db.execute(stmt)
            existing_rating = result.scalar_one_or_none()
            
            if existing_rating:
                raise ValueError("Rating already exists for this order")
            
            # Create rating
            db_rating = Rating(
                order_id=order_id,
                user_id=user_id,
                restaurant_rating=rating_data.restaurant_rating,
                delivery_rating=rating_data.delivery_rating,
                restaurant_review=rating_data.restaurant_review,
                delivery_review=rating_data.delivery_review
            )
            
            self.db.add(db_rating)
            await self.db.commit()
            
            return RatingResponse.from_orm(db_rating)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating rating: {e}")
            raise
    
    async def _notify_restaurant_service(self, order_id: UUID, restaurant_id: UUID):
        """Notify restaurant service about new order"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://restaurant-service:8000/orders/{order_id}/notify",
                    json={"restaurant_id": str(restaurant_id)},
                    timeout=5.0
                )
                if response.status_code != 200:
                    logger.warning(f"Failed to notify restaurant service: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error notifying restaurant service: {e}")
            pass