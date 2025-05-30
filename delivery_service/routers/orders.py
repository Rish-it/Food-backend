from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared.database import get_db
from delivery_service.services import OrderService
from delivery_service.schemas import DeliveryOrderResponse, DeliveryStatusUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/agent/{agent_id}", response_model=List[DeliveryOrderResponse])
async def get_agent_orders(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[DeliveryOrderResponse]:
    """Get all orders assigned to a delivery agent"""
    try:
        service = OrderService(db)
        orders = await service.get_agent_orders(agent_id)
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent orders"
        )

@router.get("/{order_id}", response_model=DeliveryOrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
) -> DeliveryOrderResponse:
    """Get order details by ID"""
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

@router.patch("/{order_id}/agent/{agent_id}/status", response_model=DeliveryOrderResponse)
async def update_delivery_status(
    order_id: str,
    agent_id: str,
    status_update: DeliveryStatusUpdate,
    db: AsyncSession = Depends(get_db)
) -> DeliveryOrderResponse:
    """Update delivery status of an order"""
    try:
        service = OrderService(db)
        order = await service.update_delivery_status(order_id, agent_id, status_update)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not assigned to this agent"
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating delivery status for order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update delivery status"
        )

@router.post("/{order_id}/agent/{agent_id}/pickup", response_model=DeliveryOrderResponse)
async def mark_order_picked_up(
    order_id: str,
    agent_id: str,
    db: AsyncSession = Depends(get_db)
) -> DeliveryOrderResponse:
    """Mark order as picked up from restaurant"""
    try:
        service = OrderService(db)
        order = await service.mark_order_picked_up(order_id, agent_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not assigned to this agent"
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking order {order_id} as picked up: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark order as picked up"
        )

@router.post("/{order_id}/agent/{agent_id}/on-the-way", response_model=DeliveryOrderResponse)
async def mark_order_on_the_way(
    order_id: str,
    agent_id: str,
    db: AsyncSession = Depends(get_db)
) -> DeliveryOrderResponse:
    """Mark order as on the way to customer"""
    try:
        service = OrderService(db)
        order = await service.mark_order_on_the_way(order_id, agent_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not assigned to this agent"
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking order {order_id} as on the way: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark order as on the way"
        )

@router.post("/{order_id}/agent/{agent_id}/delivered", response_model=DeliveryOrderResponse)
async def mark_order_delivered(
    order_id: str,
    agent_id: str,
    db: AsyncSession = Depends(get_db)
) -> DeliveryOrderResponse:
    """Mark order as delivered to customer"""
    try:
        service = OrderService(db)
        order = await service.mark_order_delivered(order_id, agent_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not assigned to this agent"
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking order {order_id} as delivered: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark order as delivered"
        ) 