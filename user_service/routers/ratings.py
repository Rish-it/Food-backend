from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from shared.database import get_db
from user_service.services import OrderService
from user_service.schemas import RatingCreate, RatingResponse
from user_service.routers.orders import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ratings", tags=["ratings"])

@router.post("/orders/{order_id}", response_model=RatingResponse, status_code=201)
async def create_rating(
    order_id: UUID,
    rating_data: RatingCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> RatingResponse:
    """
    Create a rating for a delivered order.
    
    Requires X-User-Id header for authentication.
    """
    try:
        service = OrderService(db)
        rating = await service.create_rating(user_id, order_id, rating_data)
        return rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_rating: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")