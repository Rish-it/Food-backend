from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, time
import httpx
import logging

from shared.models.restaurant import Restaurant, MenuItem
from ..schemas import RestaurantResponse

logger = logging.getLogger(__name__)

class RestaurantService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_online_restaurants(self) -> List[RestaurantResponse]:
        """Get all restaurants that are currently online and within operating hours"""
        try:
            # Query for online restaurants with their menu items
            stmt = (
                select(Restaurant)
                .options(selectinload(Restaurant.menu_items))
                .where(Restaurant.is_online == True)
            )
            
            result = await self.db.execute(stmt)
            restaurants = result.scalars().all()
            
            # Filter by operating hours
            current_time = datetime.now().time()
            current_day = datetime.now().strftime('%A').lower()
            
            online_restaurants = []
            for restaurant in restaurants:
                if self._is_restaurant_open(restaurant, current_day, current_time):
                    # Filter available menu items
                    available_items = [
                        item for item in restaurant.menu_items 
                        if item.is_available
                    ]
                    
                    restaurant_data = RestaurantResponse.from_orm(restaurant)
                    restaurant_data.menu_items = available_items
                    online_restaurants.append(restaurant_data)
            
            return online_restaurants
            
        except Exception as e:
            logger.error(f"Error fetching online restaurants: {e}")
            raise
    
    async def get_restaurant_by_id(self, restaurant_id: str) -> Optional[RestaurantResponse]:
        """Get a specific restaurant by ID"""
        try:
            stmt = (
                select(Restaurant)
                .options(selectinload(Restaurant.menu_items))
                .where(Restaurant.id == restaurant_id)
            )
            
            result = await self.db.execute(stmt)
            restaurant = result.scalar_one_or_none()
            
            if not restaurant:
                return None
                
            return RestaurantResponse.from_orm(restaurant)
            
        except Exception as e:
            logger.error(f"Error fetching restaurant {restaurant_id}: {e}")
            raise
    
    def _is_restaurant_open(self, restaurant: Restaurant, current_day: str, current_time: time) -> bool:
        """Check if restaurant is open based on operating hours"""
        if not restaurant.operation_hours:
            return True  # Assume open if no hours specified
        
        day_hours = restaurant.operation_hours.get(current_day)
        if not day_hours:
            return False  # Closed if no hours for current day
        
        try:
            open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
            close_time = datetime.strptime(day_hours['close'], '%H:%M').time()
            
            # Handle overnight hours (e.g., 22:00 to 02:00)
            if close_time < open_time:
                return current_time >= open_time or current_time <= close_time
            else:
                return open_time <= current_time <= close_time
                
        except (KeyError, ValueError):
            logger.warning(f"Invalid operating hours format for restaurant {restaurant.id}")
            return True  # Default to open if format is invalid
