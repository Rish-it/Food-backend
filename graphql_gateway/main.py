from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .schema import schema
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Food Delivery - GraphQL API Gateway",
    description="Unified GraphQL API for food delivery microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "graphql-gateway",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Food Delivery GraphQL Gateway",
        "version": "1.0.0",
        "description": "Unified GraphQL API for all food delivery services",
        "endpoints": {
            "graphql": "/graphql - Main GraphQL endpoint",
            "graphql_ide": "/graphql - GraphQL IDE for testing",
            "health": "/health - Service health check",
            "docs": "/docs - API documentation"
        },
        "services": {
            "user_service": "http://localhost:8001",
            "restaurant_service": "http://localhost:8002", 
            "delivery_service": "http://localhost:8003"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 