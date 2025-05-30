from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared.database import get_db
from restaurant_service.services import RestaurantService
from restaurant_service.schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: AsyncSession = Depends(get_db)
) -> RestaurantResponse:
    """Create a new restaurant"""
    try:
        service = RestaurantService(db)
        restaurant = await service.create_restaurant(restaurant_data)
        return restaurant
    except Exception as e:
        logger.error(f"Error creating restaurant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create restaurant"
        )

@router.get("/", response_model=List[RestaurantResponse])
async def get_restaurants(
    online_only: bool = False,
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantResponse]:
    """Get all restaurants, optionally filtered by online status"""
    try:
        service = RestaurantService(db)
        restaurants = await service.get_restaurants(online_only=online_only)
        return restaurants
    except Exception as e:
        logger.error(f"Error fetching restaurants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch restaurants"
        )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch restaurant"
        )

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: str,
    update_data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db)
) -> RestaurantResponse:
    """Update restaurant information"""
    try:
        service = RestaurantService(db)
        restaurant = await service.update_restaurant(restaurant_id, update_data)
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update restaurant"
        )

@router.patch("/{restaurant_id}/status")
async def toggle_restaurant_status(
    restaurant_id: str,
    is_online: bool,
    db: AsyncSession = Depends(get_db)
) -> RestaurantResponse:
    """Toggle restaurant online/offline status"""
    try:
        service = RestaurantService(db)
        restaurant = await service.toggle_online_status(restaurant_id, is_online)
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating restaurant status {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update restaurant status"
        )

@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete/deactivate a restaurant"""
    try:
        service = RestaurantService(db)
        success = await service.delete_restaurant(restaurant_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        return {"message": "Restaurant deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate restaurant"
        ) 