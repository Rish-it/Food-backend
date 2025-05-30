import asyncio
import sys
import os
from decimal import Decimal
from uuid import uuid4

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import AsyncSessionLocal
from shared.models import User, Restaurant, MenuItem, DeliveryAgent

async def create_test_data():
    """Create test data for the application"""
    async with AsyncSessionLocal() as db:
        try:
            # Create test users
            users = [
                User(
                    id=uuid4(),
                    email="john.doe@example.com",
                    phone="+1-555-0101",
                    name="John Doe",
                    address={
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10001",
                        "lat": 40.7128,
                        "lng": -74.0060
                    }
                ),
                User(
                    id=uuid4(),
                    email="jane.smith@example.com",
                    phone="+1-555-0102",
                    name="Jane Smith",
                    address={
                        "street": "456 Oak Ave",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10002",
                        "lat": 40.7589,
                        "lng": -73.9851
                    }
                )
            ]
            
            for user in users:
                db.add(user)
            
            # Create test restaurants
            restaurant1 = Restaurant(
                id=uuid4(),
                name="Pizza Palace",
                email="orders@pizzapalace.com",
                phone="+1-555-0201",
                address={
                    "street": "789 Broadway",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10003",
                    "lat": 40.7505,
                    "lng": -73.9934
                },
                cuisine_type="Italian",
                is_online=True,
                operating_hours={
                    "monday": {"open": "11:00", "close": "23:00"},
                    "tuesday": {"open": "11:00", "close": "23:00"},
                    "wednesday": {"open": "11:00", "close": "23:00"},
                    "thursday": {"open": "11:00", "close": "23:00"},
                    "friday": {"open": "11:00", "close": "01:00"},
                    "saturday": {"open": "11:00", "close": "01:00"},
                    "sunday": {"open": "12:00", "close": "22:00"}
                }
            )
            
            restaurant2 = Restaurant(
                id=uuid4(),
                name="Burger Barn",
                email="orders@burgerbarn.com",
                phone="+1-555-0202",
                address={
                    "street": "321 5th Ave",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10016",
                    "lat": 40.7505,
                    "lng": -73.9820
                },
                cuisine_type="American",
                is_online=True,
                operating_hours={
                    "monday": {"open": "10:00", "close": "22:00"},
                    "tuesday": {"open": "10:00", "close": "22:00"},
                    "wednesday": {"open": "10:00", "close": "22:00"},
                    "thursday": {"open": "10:00", "close": "22:00"},
                    "friday": {"open": "10:00", "close": "23:00"},
                    "saturday": {"open": "10:00", "close": "23:00"},
                    "sunday": {"open": "11:00", "close": "21:00"}
                }
            )
            
            db.add(restaurant1)
            db.add(restaurant2)
            await db.flush()  # Get restaurant IDs
            
            # Create menu items for Pizza Palace
            pizza_items = [
                MenuItem(
                    restaurant_id=restaurant1.id,
                    name="Margherita Pizza",
                    description="Fresh tomato sauce, mozzarella, and basil",
                    price=Decimal("16.99"),
                    category="Pizza",
                    is_available=True,
                    image_url="https://example.com/margherita.jpg"
                ),
                MenuItem(
                    restaurant_id=restaurant1.id,
                    name="Pepperoni Pizza",
                    description="Classic pepperoni with mozzarella cheese",
                    price=Decimal("18.99"),
                    category="Pizza",
                    is_available=True,
                    image_url="https://example.com/pepperoni.jpg"
                ),
                MenuItem(
                    restaurant_id=restaurant1.id,
                    name="Caesar Salad",
                    description="Crisp romaine lettuce with Caesar dressing",
                    price=Decimal("12.99"),
                    category="Salad",
                    is_available=True,
                    image_url="https://example.com/caesar.jpg"
                )
            ]
            
            # Create menu items for Burger Barn
            burger_items = [
                MenuItem(
                    restaurant_id=restaurant2.id,
                    name="Classic Burger",
                    description="Beef patty with lettuce, tomato, and onion",
                    price=Decimal("14.99"),
                    category="Burger",
                    is_available=True,
                    image_url="https://example.com/classic-burger.jpg"
                ),
                MenuItem(
                    restaurant_id=restaurant2.id,
                    name="Cheese Burger",
                    description="Classic burger with American cheese",
                    price=Decimal("16.99"),
                    category="Burger",
                    is_available=True,
                    image_url="https://example.com/cheese-burger.jpg"
                ),
                MenuItem(
                    restaurant_id=restaurant2.id,
                    name="French Fries",
                    description="Crispy golden french fries",
                    price=Decimal("6.99"),
                    category="Sides",
                    is_available=True,
                    image_url="https://example.com/fries.jpg"
                )
            ]
            
            for item in pizza_items + burger_items:
                db.add(item)
            
            # Create test delivery agents
            agents = [
                DeliveryAgent(
                    id=uuid4(),
                    name="Mike Wilson",
                    email="mike.wilson@delivery.com",
                    phone="+1-555-0301",
                    is_available=True,
                    current_location={"lat": 40.7505, "lng": -73.9934},
                    vehicle_type="bike"
                ),
                DeliveryAgent(
                    id=uuid4(),
                    name="Sarah Johnson",
                    email="sarah.johnson@delivery.com",
                    phone="+1-555-0302",
                    is_available=True,
                    current_location={"lat": 40.7589, "lng": -73.9851},
                    vehicle_type="scooter"
                )
            ]
            
            for agent in agents:
                db.add(agent)
            
            await db.commit()
            print("Test data created successfully!")
            
            # Print useful IDs
            print(f"\nTest User IDs:")
            for user in users:
                print(f"  {user.name}: {user.id}")
            
            print(f"\nTest Restaurant IDs:")
            print(f"  {restaurant1.name}: {restaurant1.id}")
            print(f"  {restaurant2.name}: {restaurant2.id}")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating test data: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(create_test_data())
