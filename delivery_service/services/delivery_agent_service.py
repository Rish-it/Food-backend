from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import logging
import uuid

from shared.models import DeliveryAgent
from delivery_service.schemas import (
    DeliveryAgentCreate, DeliveryAgentUpdate, DeliveryAgentResponse, LocationUpdate
)

logger = logging.getLogger(__name__)

class DeliveryAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_delivery_agent(self, agent_data: DeliveryAgentCreate) -> DeliveryAgentResponse:
        """Create a new delivery agent"""
        try:
            # Convert location to dict if provided
            location_dict = None
            if agent_data.current_location:
                location_dict = agent_data.current_location.dict()

            delivery_agent = DeliveryAgent(
                name=agent_data.name,
                email=agent_data.email,
                phone=agent_data.phone,
                vehicle_type=agent_data.vehicle_type,
                current_location=location_dict,
                is_available=True  # Default to available when created
            )
            
            self.db.add(delivery_agent)
            await self.db.commit()
            await self.db.refresh(delivery_agent)
            
            logger.info(f"Created delivery agent: {delivery_agent.name} (ID: {delivery_agent.id})")
            return DeliveryAgentResponse.model_validate(delivery_agent)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating delivery agent: {e}")
            raise

    async def get_delivery_agent_by_id(self, agent_id: str) -> Optional[DeliveryAgentResponse]:
        """Get delivery agent by ID"""
        try:
            agent_uuid = uuid.UUID(agent_id)
            
            stmt = select(DeliveryAgent).where(DeliveryAgent.id == agent_uuid)
            result = await self.db.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if agent:
                return DeliveryAgentResponse.model_validate(agent)
            return None
            
        except ValueError as e:
            logger.error(f"Invalid agent ID format: {agent_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching delivery agent {agent_id}: {e}")
            raise

    async def get_delivery_agents(self, available_only: bool = False) -> List[DeliveryAgentResponse]:
        """Get all delivery agents, optionally filtered by availability"""
        try:
            stmt = select(DeliveryAgent)
            
            if available_only:
                stmt = stmt.where(DeliveryAgent.is_available == True)
            
            result = await self.db.execute(stmt)
            agents = result.scalars().all()
            
            return [DeliveryAgentResponse.model_validate(agent) for agent in agents]
            
        except Exception as e:
            logger.error(f"Error fetching delivery agents: {e}")
            raise

    async def update_delivery_agent(self, agent_id: str, update_data: DeliveryAgentUpdate) -> Optional[DeliveryAgentResponse]:
        """Update delivery agent information"""
        try:
            agent_uuid = uuid.UUID(agent_id)
            
            update_dict = {}
            for field, value in update_data.dict(exclude_unset=True).items():
                if field == 'current_location' and value:
                    update_dict[field] = value.dict() if hasattr(value, 'dict') else value
                else:
                    update_dict[field] = value
            
            if not update_dict:
                # No fields to update
                return await self.get_delivery_agent_by_id(agent_id)
            
            stmt = update(DeliveryAgent).where(
                DeliveryAgent.id == agent_uuid
            ).values(**update_dict)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            logger.info(f"Updated delivery agent {agent_id} with fields: {list(update_dict.keys())}")
            return await self.get_delivery_agent_by_id(agent_id)
            
        except ValueError as e:
            logger.error(f"Invalid agent ID format: {agent_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating delivery agent {agent_id}: {e}")
            raise

    async def toggle_availability(self, agent_id: str, is_available: bool) -> Optional[DeliveryAgentResponse]:
        """Toggle delivery agent availability"""
        try:
            agent_uuid = uuid.UUID(agent_id)
            
            stmt = update(DeliveryAgent).where(
                DeliveryAgent.id == agent_uuid
            ).values(is_available=is_available)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            status = "available" if is_available else "unavailable"
            logger.info(f"Delivery agent {agent_id} is now {status}")
            
            return await self.get_delivery_agent_by_id(agent_id)
            
        except ValueError as e:
            logger.error(f"Invalid agent ID format: {agent_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating agent availability {agent_id}: {e}")
            raise

    async def update_location(self, agent_id: str, location: LocationUpdate) -> Optional[DeliveryAgentResponse]:
        """Update delivery agent location"""
        try:
            agent_uuid = uuid.UUID(agent_id)
            
            location_dict = location.dict()
            
            stmt = update(DeliveryAgent).where(
                DeliveryAgent.id == agent_uuid
            ).values(current_location=location_dict)
            
            result = await self.db.execute(stmt)
            
            if result.rowcount == 0:
                return None
            
            await self.db.commit()
            
            logger.info(f"Updated location for delivery agent {agent_id}")
            return await self.get_delivery_agent_by_id(agent_id)
            
        except ValueError as e:
            logger.error(f"Invalid agent ID format: {agent_id}")
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating agent location {agent_id}: {e}")
            raise

    async def get_available_agents(self) -> List[DeliveryAgentResponse]:
        """Get all available delivery agents"""
        return await self.get_delivery_agents(available_only=True) 