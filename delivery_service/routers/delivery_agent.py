from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared.database import get_db
from delivery_service.services import DeliveryAgentService
from delivery_service.schemas import (
    DeliveryAgentCreate, DeliveryAgentUpdate, DeliveryAgentResponse, LocationUpdate
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["delivery-agents"])

@router.post("/", response_model=DeliveryAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_agent(
    agent_data: DeliveryAgentCreate,
    db: AsyncSession = Depends(get_db)
) -> DeliveryAgentResponse:
    """Register a new delivery agent"""
    try:
        service = DeliveryAgentService(db)
        agent = await service.create_delivery_agent(agent_data)
        return agent
    except Exception as e:
        logger.error(f"Error creating delivery agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create delivery agent"
        )

@router.get("/", response_model=List[DeliveryAgentResponse])
async def get_delivery_agents(
    available_only: bool = False,
    db: AsyncSession = Depends(get_db)
) -> List[DeliveryAgentResponse]:
    """Get all delivery agents, optionally filtered by availability"""
    try:
        service = DeliveryAgentService(db)
        agents = await service.get_delivery_agents(available_only=available_only)
        return agents
    except Exception as e:
        logger.error(f"Error fetching delivery agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch delivery agents"
        )

@router.get("/{agent_id}", response_model=DeliveryAgentResponse)
async def get_delivery_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
) -> DeliveryAgentResponse:
    """Get a specific delivery agent by ID"""
    try:
        service = DeliveryAgentService(db)
        agent = await service.get_delivery_agent_by_id(agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery agent not found"
            )
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching delivery agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch delivery agent"
        )

@router.put("/{agent_id}", response_model=DeliveryAgentResponse)
async def update_delivery_agent(
    agent_id: str,
    update_data: DeliveryAgentUpdate,
    db: AsyncSession = Depends(get_db)
) -> DeliveryAgentResponse:
    """Update delivery agent information"""
    try:
        service = DeliveryAgentService(db)
        agent = await service.update_delivery_agent(agent_id, update_data)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery agent not found"
            )
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating delivery agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update delivery agent"
        )

@router.patch("/{agent_id}/availability")
async def toggle_agent_availability(
    agent_id: str,
    is_available: bool,
    db: AsyncSession = Depends(get_db)
) -> DeliveryAgentResponse:
    """Toggle delivery agent availability status"""
    try:
        service = DeliveryAgentService(db)
        agent = await service.toggle_availability(agent_id, is_available)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery agent not found"
            )
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent availability {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent availability"
        )

@router.put("/{agent_id}/location")
async def update_agent_location(
    agent_id: str,
    location: LocationUpdate,
    db: AsyncSession = Depends(get_db)
) -> DeliveryAgentResponse:
    """Update delivery agent location"""
    try:
        service = DeliveryAgentService(db)
        agent = await service.update_location(agent_id, location)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery agent not found"
            )
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent location {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent location"
        )

@router.get("/available/list", response_model=List[DeliveryAgentResponse])
async def get_available_agents(
    db: AsyncSession = Depends(get_db)
) -> List[DeliveryAgentResponse]:
    """Get all available delivery agents"""
    try:
        service = DeliveryAgentService(db)
        agents = await service.get_available_agents()
        return agents
    except Exception as e:
        logger.error(f"Error fetching available agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available agents"
        ) 