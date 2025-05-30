from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import uuid
import httpx
from datetime import datetime

from shared.models import Order, OrderItem, DeliveryAgent
from shared.config import settings
from restaurant_service.schemas import (
    OrderUpdateRequest, OrderStatusUpdate, DeliveryAssignment, RestaurantOrderResponse
)

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_restaurant_orders(
        self, 
        restaurant_id: str, 
        status_filter: Optional[str] = None
    ) -> List[RestaurantOrderResponse]:
        """Get all orders for a restaurant, optionally filtered by status"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = select(Order).options(
                selectinload(Order.order_items)
            ).where(Order.restaurant_id == restaurant_uuid)
            
            if status_filter:
                stmt = stmt.where(Order.status == status_filter)
            
            # Order by most recent first
            stmt = stmt.order_by(Order.placed_at.desc())
            
            result = await self.db.execute(stmt)
            orders = result.scalars().all()
            
            return [RestaurantOrderResponse.model_validate(order) for order in orders]
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching orders for restaurant {restaurant_id}: {e}")
            raise

    async def get_order_by_id(self, order_id: str) -> Optional[RestaurantOrderResponse]:
        """Get a specific order by ID"""
        try:
            order_uuid = uuid.UUID(order_id)
            
            stmt = select(Order).options(
                selectinload(Order.order_items)
            ).where(Order.id == order_uuid)
            
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if order:
                return RestaurantOrderResponse.model_validate(order)
            return None
            
        except ValueError as e:
            logger.error(f"Invalid order ID format: {order_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise

    async def update_order_status(
        self, 
        order_id: str, 
        restaurant_id: str, 
        update_request: OrderUpdateRequest
    ) -> Optional[OrderStatusUpdate]:
        """Update order status (accept/reject/preparing/ready)"""
        try:
            order_uuid = uuid.UUID(order_id)
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            # Verify order belongs to this restaurant
            order_stmt = select(Order).where(
                Order.id == order_uuid,
                Order.restaurant_id == restaurant_uuid
            )
            order_result = await self.db.execute(order_stmt)
            order = order_result.scalar_one_or_none()
            
            if not order:
                logger.error(f"Order {order_id} not found for restaurant {restaurant_id}")
                return None
            
            update_data = {
                'status': update_request.status,
                'updated_at': func.now()
            }
            
            if update_request.status == 'accepted':
                update_data['accepted_at'] = func.now()
                
                # Auto-assign delivery agent when order is accepted
                await self._auto_assign_delivery_agent(order_uuid)
            
            stmt = update(Order).where(Order.id == order_uuid).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.info(f"Updated order {order_id} status to {update_request.status}")
            
            return OrderStatusUpdate(
                order_id=order_uuid,
                status=update_request.status,
                updated_at=datetime.now(),
                estimated_prep_time=update_request.estimated_prep_time
            )
            
        except ValueError as e:
            logger.error(f"Invalid ID format: {e}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating order status: {e}")
            raise

    async def _auto_assign_delivery_agent(self, order_id: uuid.UUID) -> Optional[DeliveryAssignment]:
        """Auto-assign an available delivery agent to an order"""
        try:
            # Find available delivery agent
            agent_stmt = select(DeliveryAgent).where(
                DeliveryAgent.is_available == True
            ).limit(1)
            
            result = await self.db.execute(agent_stmt)
            delivery_agent = result.scalar_one_or_none()
            
            if not delivery_agent:
                logger.warning(f"No available delivery agents for order {order_id}")
                return None
            
            # Assign agent to order
            order_update = update(Order).where(Order.id == order_id).values(
                delivery_agent_id=delivery_agent.id
            )
            await self.db.execute(order_update)
            
            # Mark agent as unavailable
            agent_update = update(DeliveryAgent).where(
                DeliveryAgent.id == delivery_agent.id
            ).values(is_available=False)
            await self.db.execute(agent_update)
            
            await self.db.commit()
            
            assignment = DeliveryAssignment(
                order_id=order_id,
                delivery_agent_id=delivery_agent.id,
                assigned_at=datetime.now()
            )
            
            logger.info(f"Assigned delivery agent {delivery_agent.id} to order {order_id}")
            
            # Notify delivery service about the assignment
            await self._notify_delivery_service(assignment)
            
            return assignment
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error auto-assigning delivery agent: {e}")
            return None

    async def _notify_delivery_service(self, assignment: DeliveryAssignment):
        """Notify delivery service about order assignment"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.delivery_service_url}/assignments",
                    json={
                        "order_id": str(assignment.order_id),
                        "delivery_agent_id": str(assignment.delivery_agent_id),
                        "assigned_at": assignment.assigned_at.isoformat()
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully notified delivery service about assignment")
                else:
                    logger.warning(f"Failed to notify delivery service: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error notifying delivery service: {e}")
            # Don't raise exception as this is a notification, not critical

    async def get_pending_orders(self, restaurant_id: str) -> List[RestaurantOrderResponse]:
        """Get all pending orders for a restaurant"""
        return await self.get_restaurant_orders(restaurant_id, 'pending')

    async def get_active_orders(self, restaurant_id: str) -> List[RestaurantOrderResponse]:
        """Get all active orders (accepted, preparing, ready) for a restaurant"""
        try:
            restaurant_uuid = uuid.UUID(restaurant_id)
            
            stmt = select(Order).options(
                selectinload(Order.order_items)
            ).where(
                Order.restaurant_id == restaurant_uuid,
                Order.status.in_(['accepted', 'preparing', 'ready_for_pickup'])
            ).order_by(Order.accepted_at.desc())
            
            result = await self.db.execute(stmt)
            orders = result.scalars().all()
            
            return [RestaurantOrderResponse.model_validate(order) for order in orders]
            
        except ValueError as e:
            logger.error(f"Invalid restaurant ID format: {restaurant_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching active orders for restaurant {restaurant_id}: {e}")
            raise

    async def reject_order(self, order_id: str, restaurant_id: str, reason: Optional[str] = None) -> Optional[OrderStatusUpdate]:
        """Reject an order"""
        update_request = OrderUpdateRequest(status='rejected')
        result = await self.update_order_status(order_id, restaurant_id, update_request)
        
        if result:
            logger.info(f"Order {order_id} rejected by restaurant {restaurant_id}. Reason: {reason}")
        
        return result

    async def mark_order_ready(self, order_id: str, restaurant_id: str) -> Optional[OrderStatusUpdate]:
        """Mark order as ready for pickup"""
        update_request = OrderUpdateRequest(status='ready_for_pickup')
        return await self.update_order_status(order_id, restaurant_id, update_request) 