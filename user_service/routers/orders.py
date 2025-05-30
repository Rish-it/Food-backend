from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

from shared.database import get_db
from user_service.services import OrderService
from user_service.schemas import OrderCreate, OrderResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

# Mock user authentication - In production, use proper JWT authentication
async def get_current_user_id(x_user_id: str = Header(...)) -> UUID:
    """Mock authentication - extract user ID from header"""
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    """
    Create a new order.
    
    Requires X-User-Id header for authentication.
    """
    try:
        service = OrderService(db)
        order = await service.create_order(user_id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> OrderResponse:
    """Get order details by ID"""
    try:
        service = OrderService(db)
        order = await service.get_order_by_id(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Verify order belongs to user
        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    user_id: UUID = Depends(get_current_user_id),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[OrderResponse]:
    """Get all orders for the current user"""
    try:
        if limit > 100:
            limit = 100  # Prevent excessive data retrieval
        
        service = OrderService(db)
        orders = await service.get_user_orders(user_id, limit, offset)
        return orders
    except Exception as e:
        logger.error(f"Error in get_user_orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")