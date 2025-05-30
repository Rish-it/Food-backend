from .restaurant import router as restaurant_router
from .menu import router as menu_router  
from .orders import router as orders_router

__all__ = ["restaurant_router", "menu_router", "orders_router"] 