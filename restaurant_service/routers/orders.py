from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from shared.database import get_db
from restaurant_service.services import OrderService
from restaurant_service.schemas import (
    OrderUpdateRequest, OrderStatusUpdate, RestaurantOrderResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/{restaurant_id}", response_model=List[RestaurantOrderResponse])
async def get_restaurant_orders(
    restaurant_id: str,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantOrderResponse]:
    """Get all orders for a restaurant, optionally filtered by status"""
    try:
        service = OrderService(db)
        orders = await service.get_restaurant_orders(restaurant_id, status_filter)
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders for restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )

@router.get("/{restaurant_id}/pending", response_model=List[RestaurantOrderResponse])
async def get_pending_orders(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantOrderResponse]:
    """Get all pending orders for a restaurant"""
    try:
        service = OrderService(db)
        orders = await service.get_pending_orders(restaurant_id)
        return orders
    except Exception as e:
        logger.error(f"Error fetching pending orders for restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending orders"
        )

@router.get("/{restaurant_id}/active", response_model=List[RestaurantOrderResponse])
async def get_active_orders(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[RestaurantOrderResponse]:
    """Get all active orders for a restaurant"""
    try:
        service = OrderService(db)
        orders = await service.get_active_orders(restaurant_id)
        return orders
    except Exception as e:
        logger.error(f"Error fetching active orders for restaurant {restaurant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch active orders"
        )

@router.get("/order/{order_id}", response_model=RestaurantOrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
) -> RestaurantOrderResponse:
    """Get a specific order by ID"""
    try:
        service = OrderService(db)
        order = await service.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order"
        )

@router.patch("/order/{order_id}/restaurant/{restaurant_id}", response_model=OrderStatusUpdate)
async def update_order_status(
    order_id: str,
    restaurant_id: str,
    update_request: OrderUpdateRequest,
    db: AsyncSession = Depends(get_db)
) -> OrderStatusUpdate:
    """Update order status (accept/reject/preparing/ready)"""
    try:
        service = OrderService(db)
        result = await service.update_order_status(order_id, restaurant_id, update_request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not owned by this restaurant"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )

@router.post("/order/{order_id}/restaurant/{restaurant_id}/accept", response_model=OrderStatusUpdate)
async def accept_order(
    order_id: str,
    restaurant_id: str,
    estimated_prep_time: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> OrderStatusUpdate:
    """Accept an order"""
    try:
        update_request = OrderUpdateRequest(
            status='accepted',
            estimated_prep_time=estimated_prep_time
        )
        
        service = OrderService(db)
        result = await service.update_order_status(order_id, restaurant_id, update_request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not owned by this restaurant"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept order"
        )

@router.post("/order/{order_id}/restaurant/{restaurant_id}/reject", response_model=OrderStatusUpdate)
async def reject_order(
    order_id: str,
    restaurant_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> OrderStatusUpdate:
    """Reject an order"""
    try:
        service = OrderService(db)
        result = await service.reject_order(order_id, restaurant_id, reason)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not owned by this restaurant"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject order"
        )

@router.post("/order/{order_id}/restaurant/{restaurant_id}/ready", response_model=OrderStatusUpdate)
async def mark_order_ready(
    order_id: str,
    restaurant_id: str,
    db: AsyncSession = Depends(get_db)
) -> OrderStatusUpdate:
    """Mark order as ready for pickup"""
    try:
        service = OrderService(db)
        result = await service.mark_order_ready(order_id, restaurant_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not owned by this restaurant"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking order ready {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark order as ready"
        ) 