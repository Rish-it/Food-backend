from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import uuid

from shared.models import Restaurant, MenuItem
from restaurant_service.schemas import RestaurantCreate, RestaurantUpdate, RestaurantResponse

logger = logging.getLogger(__name__)

class RestaurantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_restaurant(self, restaurant_data: RestaurantCreate) -> RestaurantResponse:
        """Create a new restaurant"""
        try:
            # Convert operation_hours to dict if provided
            operation_hours_dict = None
            if restaurant_data.operation_hours:
                operation_hours_dict = restaurant_data.operation_hours.dict()

            restaurant = Restaurant(
                name=restaurant_data.name,
                email=restaurant_data.email,
                phone=restaurant_data.phone,
                address=restaurant_data.address,
                cuisine_type=restaurant_data.cuisine_type,
                operation_hours=operation_hours_dict,
                is_online=False  # Default to offline when created
            )
            
            self.db.add(restaurant)
            await self.db.commit()
            await self.db.refresh(restaurant)
            
            logger.info(f"Created restaurant: {restaurant.name} (ID: {restaurant.id})")
            
            return RestaurantResponse(
                id=restaurant.id,
                name=restaurant.name,
                email=restaurant.email,
                phone=restaurant.phone,
                address=restaurant.address,
                cuisine_type=restaurant.cuisine_type,
                operation_hours=restaurant.operation_hours,
                is_online=restaurant.is_online,
                menu_items=[],  # Empty for new restaurant
                created_at=restaurant.created_at,
                updated_at=restaurant.updated_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating restaurant: {e}")
            raise

    async def get_restaurant_by_id(self, restaurant_id: str) -> Optional[RestaurantResponse]:
        """Get restaurant by ID with menu items"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = select(Restaurant).options(
                selectinload(Restaurant.menu_items)
            ).where(Restaurant.id == restaurant_uuid)
            
            result = await self.db.execute(stmt)
            restaurant = result.scalar_one_or_none()
            
            if restaurant:
                return RestaurantResponse.model_validate(restaurant)
            return None
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching restaurant {restaurant_id}: {e}")
            raise

    async def get_restaurants(self, online_only: bool = False) -> List[RestaurantResponse]:
        """Get all restaurants, optionally filtered by online status"""
        try:
            stmt = select(Restaurant).options(
                selectinload(Restaurant.menu_items)
            )
            
            if online_only:
                stmt = stmt.where(Restaurant.is_online == True)
            
            result = await self.db.execute(stmt)
            restaurants = result.scalars().all()
            
            return [RestaurantResponse.model_validate(restaurant) for restaurant in restaurants]
            
        except Exception as e:
            logger.error(f"Error fetching restaurants: {e}")
            raise

    async def update_restaurant(self, restaurant_id: str, update_data: RestaurantUpdate) -> Optional[RestaurantResponse]:
        """Update restaurant information"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if field == 'operation_hours' and value:
                    update_dict[field] = value.dict() if hasattr(value, 'dict') else value
                else:
                    update_dict[field] = value
            
            if not update_dict:
                # No fields to update
                return await self.get_restaurant_by_id(restaurant_id)
            
            stmt = update(Restaurant).where(
                Restaurant.id == restaurant_uuid
            ).values(**update_dict)
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.info(f"Updated restaurant {restaurant_id} with fields: {list(update_dict.keys())}")
            return await self.get_restaurant_by_id(restaurant_id)
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating restaurant {restaurant_id}: {e}")
            raise

    async def toggle_online_status(self, restaurant_id: str, is_online: bool) -> Optional[RestaurantResponse]:
        """Toggle restaurant online/offline status"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = update(Restaurant).where(
                Restaurant.id == restaurant_uuid
            ).values(is_online=is_online)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            status = "online" if is_online else "offline"
            logger.info(f"Restaurant {restaurant_id} is now {status}")
            
            return await self.get_restaurant_by_id(restaurant_id)
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating restaurant status {restaurant_id}: {e}")
            raise

    async def delete_restaurant(self, restaurant_id: str) -> bool:
        """Delete a restaurant (soft delete by setting offline)"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = update(Restaurant).where(
                Restaurant.id == restaurant_uuid
            ).values(is_online=False)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return False
            
            await self.db.commit()
            logger.info(f"Deactivated restaurant {restaurant_id}")
            return True
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deactivating restaurant {restaurant_id}: {e}")
            raise 