from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared.database import get_db
from restaurant_service.services import MenuService
from restaurant_service.schemas import (
    MenuItemCreate, MenuItemUpdate, MenuItemResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/menu", tags=["menu"])

@router.post("/{restaurant_id}/items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    restaurant_id: str,
    menu_item_data: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
) -> MenuItemResponse:
    """Create a new menu item for a restaurant"""
    try:
        service = MenuService(db)
        menu_item = await service.create_menu_item(restaurant_id, menu_item_data)
        return menu_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating menu item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create menu item"
        )

@router.get("/{restaurant_id}/items", response_model=List[MenuItemResponse])
async def get_restaurant_menu(
    restaurant_id: str,
    available_only: bool = False,
    category: str = None,
    db: AsyncSession = Depends(get_db)
) -> List[MenuItemResponse]:
    """Get menu items for a restaurant"""
    try:
        service = MenuService(db)
        
        if category:
            menu_items = await service.get_menu_by_category(restaurant_id, category)
        else:
            menu_items = await service.get_restaurant_menu(restaurant_id, available_only)
        
        return menu_items
    except Exception as e:
        logger.error(f"Error fetching menu for restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch menu"
        )

@router.get("/items/{menu_item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    menu_item_id: str,
    db: AsyncSession = Depends(get_db)
) -> MenuItemResponse:
    """Get a specific menu item by ID"""
    try:
        service = MenuService(db)
        menu_item = await service.get_menu_item_by_id(menu_item_id)
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        return menu_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching menu item {menu_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch menu item"
        )

@router.put("/items/{menu_item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    menu_item_id: str,
    update_data: MenuItemUpdate,
    db: AsyncSession = Depends(get_db)
) -> MenuItemResponse:
    """Update menu item information"""
    try:
        service = MenuService(db)
        menu_item = await service.update_menu_item(menu_item_id, update_data)
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        return menu_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating menu item {menu_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update menu item"
        )

@router.patch("/items/{menu_item_id}/availability")
async def toggle_menu_item_availability(
    menu_item_id: str,
    is_available: bool,
    db: AsyncSession = Depends(get_db)
) -> MenuItemResponse:
    """Toggle menu item availability"""
    try:
        service = MenuService(db)
        menu_item = await service.toggle_menu_item_availability(menu_item_id, is_available)
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        return menu_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating menu item availability {menu_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update menu item availability"
        )

@router.delete("/items/{menu_item_id}")
async def delete_menu_item(
    menu_item_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a menu item"""
    try:
        service = MenuService(db)
        success = await service.delete_menu_item(menu_item_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        return {"message": "Menu item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting menu item {menu_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete menu item"
        ) 