"""Test configuration and fixtures for Food Delivery Microservices"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
import sys
import os
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared.database import Base, get_db
from shared.config import settings
from user_service.main import app as user_app
from restaurant_service.main import app as restaurant_app  
from delivery_service.main import app as delivery_app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/mydb_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="session")
async def setup_test_database():
    """Set up test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def user_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for User Service"""
    
    async def override_get_db():
        yield db_session
    
    user_app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=user_app, base_url="http://testserver") as client:
        yield client
    
    user_app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def restaurant_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for Restaurant Service"""
    
    async def override_get_db():
        yield db_session
    
    restaurant_app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=restaurant_app, base_url="http://testserver") as client:
        yield client
    
    restaurant_app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def delivery_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client for Delivery Service"""
    
    async def override_get_db():
        yield db_session
    
    delivery_app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=delivery_app, base_url="http://testserver") as client:
        yield client
    
    delivery_app.dependency_overrides.clear()

# Sample test data fixtures
@pytest.fixture
def sample_restaurant_data() -> Dict[str, Any]:
    """Sample restaurant data for testing"""
    return {
        "name": "Test Restaurant",
        "email": "test@restaurant.com",
        "phone": "5555555555",
        "address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345"
        },
        "cuisine_type": "Test Cuisine",
        "operation_hours": {
            "monday": {"open": "09:00", "close": "22:00"},
            "tuesday": {"open": "09:00", "close": "22:00"},
            "wednesday": {"open": "09:00", "close": "22:00"},
            "thursday": {"open": "09:00", "close": "22:00"},
            "friday": {"open": "09:00", "close": "23:00"},
            "saturday": {"open": "08:00", "close": "23:00"},
            "sunday": {"open": "10:00", "close": "21:00"}
        }
    }

@pytest.fixture
def sample_menu_item_data() -> Dict[str, Any]:
    """Sample menu item data for testing"""
    return {
        "name": "Test Burger",
        "description": "A delicious test burger",
        "price": 15.99,
        "category": "Main Course",
        "image_url": "https://example.com/burger.jpg"
    }

@pytest.fixture
def sample_delivery_agent_data() -> Dict[str, Any]:
    """Sample delivery agent data for testing"""
    return {
        "name": "Test Agent",
        "email": "agent@test.com",
        "phone": "5555551234",
        "vehicle_type": "motorcycle",
        "current_location": {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "address": "San Francisco, CA"
        }
    }

@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing"""
    return {
        "email": "test@user.com",
        "phone": "5555555555",
        "name": "Test User",
        "address": {
            "street": "456 User St",
            "city": "User City",
            "state": "US",
            "zip_code": "54321"
        }
    }

@pytest.fixture
def sample_order_data() -> Dict[str, Any]:
    """Sample order data for testing"""
    return {
        "delivery_address": {
            "street": "789 Order St",
            "city": "Order City",
            "state": "OR",
            "zip_code": "67890"
        },
        "special_instructions": "Test order - please handle with care"
    } 