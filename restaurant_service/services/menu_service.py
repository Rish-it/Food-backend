from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import logging
import uuid

from shared.models import MenuItem, Restaurant
from restaurant_service.schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse

logger = logging.getLogger(__name__)

class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_menu_item(self, restaurant_id: str, menu_item_data: MenuItemCreate) -> MenuItemResponse:
        """Create a new menu item for a restaurant"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            # Verify restaurant exists
            restaurant_stmt = select(Restaurant).where(Restaurant.id == restaurant_uuid)
            restaurant_result = await self.db.execute(restaurant_stmt)
            restaurant = restaurant_result.scalar_one_or_none()
            
            if not restaurant:
                raise ValueError(f"Restaurant {restaurant_id} not found")

            menu_item = MenuItem(
                restaurant_id=restaurant_uuid,
                name=menu_item_data.name,
                description=menu_item_data.description,
                price=menu_item_data.price,
                category=menu_item_data.category,
                image_url=menu_item_data.image_url,
                is_available=True  # Default to available
            )
            
            self.db.add(menu_item)
            await self.db.commit()
            await self.db.refresh(menu_item)
            
            logger.info(f"Created menu item: {menu_item.name} for restaurant {restaurant_id}")
            return MenuItemResponse.model_validate(menu_item)
            
        except ValueError as e:
            logger.error(f"Invalid data for menu item creation: {e}")
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating menu item: {e}")
            raise

    async def get_menu_item_by_id(self, menu_item_id: str) -> Optional[MenuItemResponse]:
        """Get menu item by ID"""
        try:
            menu_item_uuid = uuid.UUID(menu_item_id)
            
            stmt = select(MenuItem).where(MenuItem.id == menu_item_uuid)
            result = await self.db.execute(stmt)
            menu_item = result.scalar_one_or_none()
            
            if menu_item:
                return MenuItemResponse.model_validate(menu_item)
            return None
            
        except ValueError as e:
            logger.error(f"Invalid menu item ID format: {menu_item_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching menu item {menu_item_id}: {e}")
            raise

    async def get_restaurant_menu(self, restaurant_id: str, available_only: bool = False) -> List[MenuItemResponse]:
        """Get all menu items for a restaurant"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = select(MenuItem).where(MenuItem.restaurant_id == restaurant_uuid)
            
            if available_only:
                stmt = stmt.where(MenuItem.is_available == True)
            
            result = await self.db.execute(stmt)
            menu_items = result.scalars().all()
            
            return [MenuItemResponse.model_validate(item) for item in menu_items]
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching menu for restaurant {restaurant_id}: {e}")
            raise

    async def update_menu_item(self, menu_item_id: str, update_data: MenuItemUpdate) -> Optional[MenuItemResponse]:
        """Update menu item information"""
        try:
            menu_item_uuid = uuid.UUID(menu_item_id)
            
            update_dict = update_data.dict(exclude_unset=True)
            
            if not update_dict:
                # No fields to update
                return await self.get_menu_item_by_id(menu_item_id)
            
            stmt = update(MenuItem).where(
                MenuItem.id == menu_item_uuid
            ).values(**update_dict)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            logger.info(f"Updated menu item {menu_item_id} with fields: {list(update_dict.keys())}")
            return await self.get_menu_item_by_id(menu_item_id)
            
        except ValueError as e:
            logger.error(f"Invalid menu item ID format: {menu_item_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating menu item {menu_item_id}: {e}")
            raise

    async def toggle_menu_item_availability(self, menu_item_id: str, is_available: bool) -> Optional[MenuItemResponse]:
        """Toggle menu item availability"""
        try:
            menu_item_uuid = uuid.UUID(menu_item_id)
            
            stmt = update(MenuItem).where(
                MenuItem.id == menu_item_uuid
            ).values(is_available=is_available)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            status = "available" if is_available else "unavailable"
            logger.info(f"Menu item {menu_item_id} is now {status}")
            
            return await self.get_menu_item_by_id(menu_item_id)
            
        except ValueError as e:
            logger.error(f"Invalid menu item ID format: {menu_item_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating menu item availability {menu_item_id}: {e}")
            raise

    async def delete_menu_item(self, menu_item_id: str) -> bool:
        """Delete a menu item"""
        try:
            menu_item_uuid = uuid.UUID(menu_item_id)
            
            stmt = delete(MenuItem).where(MenuItem.id == menu_item_uuid)
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return False
            
            await self.db.commit()
            logger.info(f"Deleted menu item {menu_item_id}")
            return True
            
        except ValueError as e:
            logger.error(f"Invalid menu item ID format: {menu_item_id}")
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting menu item {menu_item_id}: {e}")
            raise

    async def get_menu_by_category(self, restaurant_id: str, category: str) -> List[MenuItemResponse]:
        """Get menu items by category for a restaurant"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = select(MenuItem).where(
                MenuItem.restaurant_id == restaurant_uuid,
                MenuItem.category == category,
                MenuItem.is_available == True
            )
            
            result = await self.db.execute(stmt)
            menu_items = result.scalars().all()
            
            return [MenuItemResponse.model_validate(item) for item in menu_items]
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching menu by category for restaurant {restaurant_id}: {e}")
            raise 