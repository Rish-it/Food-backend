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
from user_service.routers import restaurants_router, orders_router, ratings_router

from strawberry.fastapi import GraphQLRouter
from user_service.gql import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("User Service starting up...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("User Service startup complete")
    
    yield
    
    logger.info("User Service shutting down...")
    await engine.dispose()
    logger.info("User Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Food Delivery - User Service",
    description="User service for food delivery application - handles restaurant listing, order placement, and ratings",
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

app.include_router(restaurants_router)
app.include_router(orders_router)
app.include_router(ratings_router)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "user-service",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Food Delivery User Service",
        "version": "1.0.0",
        "description": "Handles restaurant discovery, order placement, and user ratings",
        "endpoints": {
            "restaurants": "/restaurants - List online restaurants and view menus",
            "orders": "/orders - Place and track orders",
            "ratings": "/ratings - Leave ratings for restaurants and delivery",
            "graphql": "/graphql - GraphQL API endpoint",
            "health": "/health - Service health check",
            "docs": "/docs - API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.user_service_port,
        reload=True,
        log_level="info"
    )
