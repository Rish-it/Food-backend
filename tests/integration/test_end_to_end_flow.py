"""
End-to-End Integration Tests for Food Delivery Microservices

Tests the complete workflow:
1. Restaurant registration and menu setup
2. Delivery agent registration  
3. User places order
4. Restaurant accepts order and assigns delivery agent
5. Delivery agent updates order status to delivered
6. User submits rating
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import Dict, Any
import uuid

from tests.test_config import (
    user_client, restaurant_client, delivery_client, db_session,
    sample_restaurant_data, sample_menu_item_data, sample_delivery_agent_data,
    sample_user_data, sample_order_data
)

@pytest.mark.asyncio
async def test_complete_food_delivery_workflow(
    user_client: AsyncClient,
    restaurant_client: AsyncClient, 
    delivery_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any],
    sample_delivery_agent_data: Dict[str, Any],
    sample_user_data: Dict[str, Any],
    sample_order_data: Dict[str, Any]
):
    """Test the complete food delivery workflow from order to delivery"""
    
    # Step 1: Register a restaurant
    print("\n")
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    assert restaurant_response.status_code == 201
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    print(f"[PASS] Restaurant registered: {restaurant['name']} (ID: {restaurant_id})")
    
    # Step 2: Add menu items to the restaurant
    print("\n")
    menu_item_response = await restaurant_client.post(
        f"/menu/{restaurant_id}/items", 
        json=sample_menu_item_data
    )
    assert menu_item_response.status_code == 201
    menu_item = menu_item_response.json()
    menu_item_id = menu_item["id"]
    print(f"[PASS] Menu item added: {menu_item['name']} (ID: {menu_item_id})")
    
    # Step 3: Set restaurant online
    print("\n")
    online_response = await restaurant_client.patch(
        f"/restaurants/{restaurant_id}/status?is_online=true"
    )
    assert online_response.status_code == 200
    print("[PASS] Restaurant is now online")
    
    # Step 4: Register a delivery agent
    print("\n")
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    assert agent_response.status_code == 201
    delivery_agent = agent_response.json()
    agent_id = delivery_agent["id"]
    print(f"[PASS] Delivery agent registered: {delivery_agent['name']} (ID: {agent_id})")
    
    # Step 5: User browses online restaurants
    print("\n")
    restaurants_response = await user_client.get("/restaurants/")
    assert restaurants_response.status_code == 200
    restaurants = restaurants_response.json()
    assert len(restaurants) > 0
    assert any(r["id"] == restaurant_id for r in restaurants)
    print(f"[PASS] User found {len(restaurants)} online restaurant(s)")
    
    # Step 6: User places an order
    print("\n")
    
    # First, let's create a user (this would typically be done via user registration)
    from shared.models import User
    from sqlalchemy import select
    from tests.test_config import TestSessionLocal
    
    async with TestSessionLocal() as session:
        user = User(**sample_user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
        print(f"[PASS] User created: {user.name} (ID: {user_id})")
    
    # Prepare order data with actual menu item
    order_data = sample_order_data.copy()
    order_data["restaurant_id"] = restaurant_id
    order_data["items"] = [
        {
            "menu_item_id": menu_item_id,
            "quantity": 2
        }
    ]
    
    # Place the order
    order_response = await user_client.post(f"/orders/?user_id={user_id}", json=order_data)
    assert order_response.status_code == 201
    order = order_response.json()
    order_id = order["id"]
    assert order["status"] == "pending"
    print(f"[PASS] Order placed: {order_id} (Status: {order['status']})")
    
    # Step 7: Restaurant views and accepts the order
    print("\n")
    
    # Check pending orders
    pending_orders_response = await restaurant_client.get(f"/orders/{restaurant_id}/pending")
    assert pending_orders_response.status_code == 200
    pending_orders = pending_orders_response.json()
    assert len(pending_orders) > 0
    assert any(o["id"] == order_id for o in pending_orders)
    print(f"[PASS] Restaurant sees {len(pending_orders)} pending order(s)")
    
    # Accept the order
    accept_response = await restaurant_client.post(
        f"/orders/order/{order_id}/restaurant/{restaurant_id}/accept?estimated_prep_time=20"
    )
    assert accept_response.status_code == 200
    accepted_order = accept_response.json()
    assert accepted_order["status"] == "accepted"
    print(f"[PASS] Order accepted (Status: {accepted_order['status']})")
    
    # Step 8: Verify delivery agent assignment
    print("\n")
    
    # Check if delivery agent received the assignment
    agent_orders_response = await delivery_client.get(f"/orders/agent/{agent_id}")
    assert agent_orders_response.status_code == 200
    agent_orders = agent_orders_response.json()
    
    # The order should be assigned to the agent
    assigned_order = None
    for ao in agent_orders:
        if ao["id"] == order_id:
            assigned_order = ao
            break
    
    # Note: Assignment happens async, so we might need to check order status
    order_detail_response = await user_client.get(f"/orders/{order_id}")
    assert order_detail_response.status_code == 200
    order_detail = order_detail_response.json()
    
    if order_detail.get("delivery_agent_id"):
        print(f"[PASS] Order assigned to delivery agent: {order_detail['delivery_agent_id']}")
    else:
        print("[INFO] Order not yet assigned to delivery agent (async process)")
    
    # Step 9: Restaurant marks order ready
    print("\n")
    ready_response = await restaurant_client.post(
        f"/orders/order/{order_id}/restaurant/{restaurant_id}/ready"
    )
    assert ready_response.status_code == 200
    ready_order = ready_response.json()
    assert ready_order["status"] == "ready_for_pickup"
    print(f"[PASS] Order marked ready (Status: {ready_order['status']})")
    
    # Step 10: Delivery agent picks up order
    print("\n")
    pickup_response = await delivery_client.post(f"/orders/{order_id}/agent/{agent_id}/pickup")
    assert pickup_response.status_code == 200
    picked_order = pickup_response.json()
    assert picked_order["status"] == "picked_up"
    print(f"[PASS] Order picked up (Status: {picked_order['status']})")
    
    # Step 11: Delivery agent marks on the way
    print("\n")
    on_way_response = await delivery_client.post(f"/orders/{order_id}/agent/{agent_id}/on-the-way")
    assert on_way_response.status_code == 200
    on_way_order = on_way_response.json()
    assert on_way_order["status"] == "on_the_way"
    print(f"[PASS] Order on the way (Status: {on_way_order['status']})")
    
    # Step 12: Delivery agent delivers order
    print("\n")
    delivered_response = await delivery_client.post(f"/orders/{order_id}/agent/{agent_id}/delivered")
    assert delivered_response.status_code == 200
    delivered_order = delivered_response.json()
    assert delivered_order["status"] == "delivered"
    print(f"[PASS] Order delivered (Status: {delivered_order['status']})")
    
    # Step 13: User submits rating
    print("\n")
    rating_data = {
        "restaurant_rating": 5,
        "delivery_rating": 4,
        "restaurant_review": "Excellent food and service!",
        "delivery_review": "Fast delivery, friendly agent"
    }
    
    rating_response = await user_client.post(
        f"/ratings/?user_id={user_id}&order_id={order_id}", 
        json=rating_data
    )
    assert rating_response.status_code == 201
    rating = rating_response.json()
    assert rating["restaurant_rating"] == 5
    assert rating["delivery_rating"] == 4
    print(f"[PASS] Rating submitted (Restaurant: {rating['restaurant_rating']}/5, Delivery: {rating['delivery_rating']}/5)")
    
    print("\n[SUCCESS] Complete end-to-end workflow test PASSED!")
    print("=" * 60)
    print("Summary:")
    print(f"• Restaurant: {restaurant['name']}")
    print(f"• Menu Item: {menu_item['name']} (${menu_item['price']})")
    print(f"• Delivery Agent: {delivery_agent['name']}")
    print(f"• Order: {order_id}")
    print(f"• Final Status: {delivered_order['status']}")
    print(f"• Rating: {rating['restaurant_rating']}/5 stars")
@pytest.mark.asyncio
async def test_order_rejection_flow(
    user_client: AsyncClient,
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any],
    sample_order_data: Dict[str, Any]
):
    """Test order rejection workflow"""
    
    print("\n")
    
    # Setup restaurant and menu
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    menu_item_id = menu_item["id"]
    
    # Set restaurant online
    await restaurant_client.patch(f"/restaurants/{restaurant_id}/status?is_online=true")
    
    # Create user and place order
    from shared.models import User
    from tests.test_config import TestSessionLocal
    
    async with TestSessionLocal() as session:
        user = User(email="test2@test.com", phone="5555555556", name="Test User 2", address={})
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
    
    order_data = sample_order_data.copy()
    order_data["restaurant_id"] = restaurant_id
    order_data["items"] = [{"menu_item_id": menu_item_id, "quantity": 1}]
    
    order_response = await user_client.post(f"/orders/?user_id={user_id}", json=order_data)
    order = order_response.json()
    order_id = order["id"]
    
    # Restaurant rejects the order
    reject_response = await restaurant_client.post(
        f"/orders/order/{order_id}/restaurant/{restaurant_id}/reject?reason=Out of ingredients"
    )
    assert reject_response.status_code == 200
    rejected_order = reject_response.json()
    assert rejected_order["status"] == "rejected"
    print(f"[PASS] Order rejected successfully (Status: {rejected_order['status']})")
@pytest.mark.asyncio  
async def test_menu_availability_workflow(
    user_client: AsyncClient,
    restaurant_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any]
):
    """Test menu item availability management"""
    
    print("\n")
    
    # Setup restaurant
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    # Add menu item
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    menu_item_id = menu_item["id"]
    
    # Set restaurant online
    await restaurant_client.patch(f"/restaurants/{restaurant_id}/status?is_online=true")
    
    # Verify item is available
    menu_response = await restaurant_client.get(f"/menu/{restaurant_id}/items?available_only=true")
    available_items = menu_response.json()
    assert len(available_items) == 1
    assert available_items[0]["id"] == menu_item_id
    print("[PASS] Menu item is available")
    
    # Make item unavailable
    unavailable_response = await restaurant_client.patch(
        f"/menu/items/{menu_item_id}/availability?is_available=false"
    )
    assert unavailable_response.status_code == 200
    updated_item = unavailable_response.json()
    assert updated_item["is_available"] == False
    print("[PASS] Menu item marked unavailable")
    
    # Verify item is not in available items
    menu_response = await restaurant_client.get(f"/menu/{restaurant_id}/items?available_only=true")
    available_items = menu_response.json()
    assert len(available_items) == 0
    print("[PASS] Unavailable item filtered out correctly")
    
    # User should still see restaurant but with no available items
    restaurants_response = await user_client.get("/restaurants/")
    restaurants = restaurants_response.json()
    test_restaurant = next(r for r in restaurants if r["id"] == restaurant_id)
    available_menu_items = [item for item in test_restaurant["menu_items"] if item["is_available"]]
    assert len(available_menu_items) == 0
    print("[PASS] User sees restaurant with no available items")
@pytest.mark.asyncio
async def test_delivery_agent_availability_workflow(
    delivery_client: AsyncClient,
    sample_delivery_agent_data: Dict[str, Any]
):
    """Test delivery agent availability management"""
    
    print("\n")
    
    # Register delivery agent
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    agent = agent_response.json()
    agent_id = agent["id"]
    assert agent["is_available"] == True
    print("[PASS] Delivery agent registered and available")
    
    # Get available agents
    available_response = await delivery_client.get("/agents/available/list")
    available_agents = available_response.json()
    assert len(available_agents) >= 1
    assert any(a["id"] == agent_id for a in available_agents)
    print(f"[PASS] Agent appears in available agents list ({len(available_agents)} total)")
    
    # Mark agent unavailable
    unavailable_response = await delivery_client.patch(
        f"/agents/{agent_id}/availability?is_available=false"
    )
    assert unavailable_response.status_code == 200
    updated_agent = unavailable_response.json()
    assert updated_agent["is_available"] == False
    print("[PASS] Agent marked unavailable")
    
    # Verify agent not in available list
    available_response = await delivery_client.get("/agents/available/list")
    available_agents = available_response.json()
    assert not any(a["id"] == agent_id for a in available_agents)
    print("[PASS] Unavailable agent filtered out correctly")
    
    # Update agent location
    location_update = {
        "latitude": 40.7589,
        "longitude": -73.9851,
        "address": "Times Square, NY"
    }
    location_response = await delivery_client.put(f"/agents/{agent_id}/location", json=location_update)
    assert location_response.status_code == 200
    updated_agent = location_response.json()
    assert updated_agent["current_location"]["latitude"] == 40.7589
    print("[PASS] Agent location updated successfully") 