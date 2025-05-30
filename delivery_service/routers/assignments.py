from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from shared.database import get_db
from delivery_service.services import OrderService
from delivery_service.schemas import AssignmentRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.post("/", status_code=status.HTTP_200_OK)
async def receive_order_assignment(
    assignment: AssignmentRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Receive order assignment from restaurant service"""
    try:
        service = OrderService(db)
        success = await service.receive_assignment(assignment)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process order assignment"
            )
        
        return {
            "message": "Order assignment received successfully",
            "order_id": str(assignment.order_id),
            "agent_id": str(assignment.delivery_agent_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing assignment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process assignment"
        )