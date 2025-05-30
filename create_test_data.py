import asyncio
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Add shared directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from shared.database import AsyncSessionLocal, get_db
from shared.models.user import User
from shared.models.restaurant import Restaurant, MenuItem, Order, OrderItem, DeliveryAgent, Rating
from sqlalchemy.ext.asyncio import AsyncSession

async def create_test_data():
    """Create test data for the food delivery system"""
    print("Creating test data...")
    
    async for db in get_db():
        try:
            users = []
            for i in range(5):
                user = User(
                    email=f"user{i}@example.com",
                    hashed_password="test123",  # In production, this should be properly hashed
                    full_name=f"Test User {i}",
                    phone_number=f"+1234567890{i}",
                    address=f"{i}23 Test Street"
                )
                db.add(user)
                users.append(user)
            
            await db.commit()
            print("[PASS] Created test users")
            
            restaurants = []
            for i in range(3):
                restaurant = Restaurant(
                    name=f"Test Restaurant {i}",
                    description=f"A test restaurant {i}",
                    address=f"{i}45 Food Street",
                    phone_number=f"+1987654321{i}",
                    email=f"restaurant{i}@example.com",
                    is_active=True
                )
                db.add(restaurant)
                restaurants.append(restaurant)
            
            await db.commit()
            print("[PASS] Created test restaurants")
            
            menu_items = []
            for restaurant in restaurants:
                for i in range(5):
                    item = MenuItem(
                        restaurant_id=restaurant.id,
                        name=f"Test Item {i}",
                        description=f"A test menu item {i}",
                        price=random.uniform(5.0, 25.0),
                        is_available=True
                    )
                    db.add(item)
                    menu_items.append(item)
            
            await db.commit()
            print("[PASS] Created test menu items")
            
            agents = []
            for i in range(3):
                agent = DeliveryAgent(
                    name=f"Test Agent {i}",
                    phone_number=f"+1122334455{i}",
                    email=f"agent{i}@example.com",
                    is_available=True
                )
                db.add(agent)
                agents.append(agent)
            
            await db.commit()
            print("[PASS] Created test delivery agents")
            
            orders = []
            for user in users:
                for _ in range(2):  # 2 orders per user
                    order = Order(
                        user_id=user.id,
                        restaurant_id=random.choice(restaurants).id,
                        delivery_agent_id=random.choice(agents).id,
                        status="delivered",
                        total_amount=0.0,  # Will be updated after adding items
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    )
                    db.add(order)
                    orders.append(order)
            
            await db.commit()
            print("[PASS] Created test orders")
            
            for order in orders:
                total = 0.0
                for _ in range(random.randint(1, 3)):  # 1-3 items per order
                    item = random.choice(menu_items)
                    quantity = random.randint(1, 3)
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=item.id,
                        quantity=quantity,
                        price=item.price
                    )
                    total += item.price * quantity
                    db.add(order_item)
                order.total_amount = total
            
            await db.commit()
            print("[PASS] Added items to orders")
            
            for order in orders:
                rating = Rating(
                    user_id=order.user_id,
                    restaurant_id=order.restaurant_id,
                    order_id=order.id,
                    rating=random.randint(1, 5),
                    comment=f"Test rating for order {order.id}"
                )
                db.add(rating)
            
            await db.commit()
            print("[PASS] Created test ratings")
            
            print("\n[SUCCESS] Test data creation completed successfully!")
            return True
            
        except Exception as e:
            print(f"[FAIL] Error creating test data: {e}")
            await db.rollback()
            return False

if __name__ == "__main__":
    asyncio.run(create_test_data()) 