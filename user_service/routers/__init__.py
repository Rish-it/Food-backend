from .restaurants import router as restaurants_router
from .orders import router as orders_router
from .ratings import router as ratings_router

__all__ = ["restaurants_router", "orders_router", "ratings_router"]