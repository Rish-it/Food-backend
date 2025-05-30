from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from shared.models import Order, DeliveryAgent
from delivery_service.schemas import (
    DeliveryOrderResponse, DeliveryStatusUpdate, AssignmentRequest
)

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def receive_assignment(self, assignment: AssignmentRequest) -> bool:
        """Receive order assignment from restaurant service"""
        try:
            # Verify order exists
            order_stmt = select(Order).where(Order.id == assignment.order_id)
            order_result = await self.db.execute(order_stmt)
            order = order_result.scalar_one_or_none()
            
            if not order:
                logger.error(f"Order {assignment.order_id} not found")
                return False
            
            # Verify delivery agent exists and is available
            agent_stmt = select(DeliveryAgent).where(
                DeliveryAgent.id == assignment.delivery_agent_id,
                DeliveryAgent.is_available == False  # Should be marked unavailable by restaurant service
            )
            agent_result = await self.db.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            
            if not agent:
                logger.error(f"Delivery agent {assignment.delivery_agent_id} not found or available")
                return False
            order_update = update(Order).where(Order.id == assignment.order_id).values(
                status='assigned',
                updated_at=func.now()
            )
            await self.db.execute(order_update)
            await self.db.commit()
            
            logger.info(f"Successfully assigned order {assignment.order_id} to agent {assignment.delivery_agent_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error receiving assignment: {e}")
            return False

    async def get_agent_orders(self, agent_id: str) -> List[DeliveryOrderResponse]:
        """Get all orders assigned to a delivery agent"""
        try:
            agent_uuid = uuid.UUID(agent_id)
            
            stmt = select(Order).where(
                Order.delivery_agent_id == agent_uuid,
                Order.status.in_(['assigned', 'picked_up', 'on_the_way'])
            ).order_by(Order.accepted_at.desc())
            
            result = await self.db.execute(stmt)
            orders = result.scalars().all()
            
            return [DeliveryOrderResponse.model_validate(order) for order in orders]
            
        except ValueError as e:
            logger.error(f"Invalid agent ID format: {agent_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching orders for agent {agent_id}: {e}")
            raise

    async def update_delivery_status(
        self, 
        order_id: str, 
        agent_id: str, 
        status_update: DeliveryStatusUpdate
    ) -> Optional[DeliveryOrderResponse]:
        """Update delivery status of an order"""
        try:
            order_uuid = uuid.UUID(order_id)
            agent_uuid = uuid.UUID(agent_id)
            
            # Verify order belongs to this agent
            order_stmt = select(Order).where(
                Order.id == order_uuid,
                Order.delivery_agent_id == agent_uuid
            )
            order_result = await self.db.execute(order_stmt)
            order = order_result.scalar_one_or_none()
            
            if not order:
                logger.error(f"Order {order_id} not found for agent {agent_id}")
                return None
            
            update_data = {
                'status': status_update.status,
                'updated_at': func.now()
            }
            
            if status_update.status == 'delivered':
                update_data['delivered_at'] = func.now()
                
                # Mark delivery agent as available again
                agent_update = update(DeliveryAgent).where(
                    DeliveryAgent.id == agent_uuid
                ).values(is_available=True)
                await self.db.execute(agent_update)
            
            stmt = update(Order).where(Order.id == order_uuid).values(**update_data)
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.info(f"Updated order {order_id} status to {status_update.status}")
            
            updated_order_stmt = select(Order).where(Order.id == order_uuid)
            updated_result = await self.db.execute(updated_order_stmt)
            updated_order = updated_result.scalar_one()
            
            return DeliveryOrderResponse.model_validate(updated_order)
            
        except ValueError as e:
            logger.error(f"Invalid ID format: {e}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating delivery status: {e}")
            raise

    async def get_order_by_id(self, order_id: str) -> Optional[DeliveryOrderResponse]:
        """Get order details by ID"""
        try:
            order_uuid = uuid.UUID(order_id)
            
            stmt = select(Order).where(Order.id == order_uuid)
            result = await self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if order:
                return DeliveryOrderResponse.model_validate(order)
            return None
            
        except ValueError as e:
            logger.error(f"Invalid order ID format: {order_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise

    async def mark_order_picked_up(self, order_id: str, agent_id: str) -> Optional[DeliveryOrderResponse]:
        """Mark order as picked up from restaurant"""
        status_update = DeliveryStatusUpdate(status='picked_up')
        return await self.update_delivery_status(order_id, agent_id, status_update)

    async def mark_order_on_the_way(self, order_id: str, agent_id: str) -> Optional[DeliveryOrderResponse]:
        """Mark order as on the way to customer"""
        status_update = DeliveryStatusUpdate(status='on_the_way')
        return await self.update_delivery_status(order_id, agent_id, status_update)

    async def mark_order_delivered(self, order_id: str, agent_id: str) -> Optional[DeliveryOrderResponse]:
        """Mark order as delivered to customer"""
        status_update = DeliveryStatusUpdate(status='delivered')
        return await self.update_delivery_status(order_id, agent_id, status_update)