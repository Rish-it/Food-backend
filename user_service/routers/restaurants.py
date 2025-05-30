from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared.database import get_db
from user_service.services import RestaurantService
from user_service.schemas import RestaurantResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/", response_model=List[RestaurantResponse])
async def get_online_restaurants(
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantResponse]:
    """
    Get all restaurants that are currently online and open.
    
    Returns restaurants with their available menu items.
    """
    try:
        service = RestaurantService(db)
        restaurants = await service.get_online_restaurants()
        return restaurants
    except Exception as e:
        logger.error(f"Error in get_online_restaurants: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db)
) -> RestaurantResponse:
    """Get a specific restaurant by ID"""
    try:
        service = RestaurantService(db)
        restaurant = await service.get_restaurant_by_id(restaurant_id)
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_restaurant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
