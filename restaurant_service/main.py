from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add shared directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import engine, Base
from shared.config import settings
from restaurant_service.routers import restaurant_router, menu_router, orders_router

from strawberry.fastapi import GraphQLRouter
from restaurant_service.gql import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Restaurant Service starting up...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Restaurant Service startup complete")
    
    yield
    
    logger.info("Restaurant Service shutting down...")
    await engine.dispose()
    logger.info("Restaurant Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Food Delivery - Restaurant Service",
    description="Restaurant service for food delivery application",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(orders_router)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "restaurant-service",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Food Delivery Restaurant Service",
        "version": "1.0.0",
        "endpoints": {
            "restaurants": "/restaurants",
            "menu": "/menu",
            "orders": "/orders",
            "graphql": "/graphql - GraphQL API endpoint",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.restaurant_service_port,
        reload=True,
        log_level="info"
    ) 