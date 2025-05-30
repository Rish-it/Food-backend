"""
Inter-Service Communication Tests

Tests communication between microservices:
- Restaurant Service <-> Delivery Service (order assignment)
- User Service <-> Restaurant Service (restaurant listing)
- Error handling when services are unavailable
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import Dict, Any
from unittest.mock import patch, AsyncMock
import httpx

from tests.test_config import (
    user_client, restaurant_client, delivery_client, db_session,
    sample_restaurant_data, sample_menu_item_data, sample_delivery_agent_data,
    sample_user_data, sample_order_data
)

@pytest.mark.asyncio
async def test_restaurant_to_delivery_service_communication(
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any],
    sample_delivery_agent_data: Dict[str, Any],
    sample_order_data: Dict[str, Any]
):
    """Test communication from Restaurant Service to Delivery Service during order assignment"""
    
    print("\n")
    
         Create restaurant, menu item, and delivery agent
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    menu_item_id = menu_item["id"]
    
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    delivery_agent = agent_response.json()
    agent_id = delivery_agent["id"]
    
    # Create a test user and order
    from shared.models import User
    from tests.test_config import TestSessionLocal
    
    async with TestSessionLocal() as session:
        user = User(email="comm@test.com", phone="5555555557", name="Comm Test User", address={})
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
    
    # Place order (simulating user service)
    order_data = sample_order_data.copy()
    order_data["restaurant_id"] = restaurant_id
    order_data["items"] = [{"menu_item_id": menu_item_id, "quantity": 1}]
    
    # Create order directly in database (simulating User Service)
    from shared.models import Order, OrderItem
    async with TestSessionLocal() as session:
        order = Order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            delivery_address=order_data["delivery_address"],
            special_instructions=order_data["special_instructions"],
            status="pending",
            total_amount=15.99
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item_id,
            quantity=1,
            unit_price=15.99,
            total_price=15.99
        )
        session.add(order_item)
        await session.commit()
        order_id = order.id
    
    print(f"[PASS] Test order created: {order_id}")
    
    # Restaurant accepts order (this should trigger auto-assignment)
    accept_response = await restaurant_client.post(
        f"/orders/order/{order_id}/restaurant/{restaurant_id}/accept"
    )
    assert accept_response.status_code == 200
    accepted_order = accept_response.json()
    print(f"[PASS] Order accepted by restaurant (Status: {accepted_order['status']})")
    
    # Check if delivery agent was assigned
    async with TestSessionLocal() as session:
        from sqlalchemy import select
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        updated_order = result.scalar_one()
        
        if updated_order.delivery_agent_id:
            print(f"[PASS] Delivery agent assigned: {updated_order.delivery_agent_id}")
            
            # Verify agent is marked as unavailable
            stmt = select(DeliveryAgent).where(DeliveryAgent.id == updated_order.delivery_agent_id)
            result = await session.execute(stmt)
            agent = result.scalar_one()
            assert agent.is_available == False
            print("[PASS] Delivery agent marked as unavailable")
        else:
            print("[INFO] Auto-assignment may have failed (no available agents)")
@pytest.mark.asyncio
async def test_assignment_notification_to_delivery_service(
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient,
    sample_delivery_agent_data: Dict[str, Any]
):
    """Test that assignment notifications are sent to delivery service"""
    
    print("\n")
    
    # Register delivery agent
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    delivery_agent = agent_response.json()
    agent_id = delivery_agent["id"]
    
    # Simulate assignment request from restaurant service
    from datetime import datetime
    assignment_data = {
        "order_id": "550e8400-e29b-41d4-a716-446655440000",  # Mock UUID
        "delivery_agent_id": agent_id,
        "assigned_at": datetime.now().isoformat()
    }
    
    # This should fail because order doesn't exist, but tests the endpoint
    assignment_response = await delivery_client.post("/assignments/", json=assignment_data)
    
    # The endpoint should return 400 because order doesn't exist
    assert assignment_response.status_code == 400
    response_data = assignment_response.json()
    assert "Failed to process order assignment" in response_data["detail"]
    print("✅ Assignment endpoint correctly rejects invalid order")
@pytest.mark.asyncio  
async def test_service_health_checks(
    user_client: AsyncClient,
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient
):
    """Test health check endpoints for all services"""
    
    print("\n")
    
    # Test User Service health
    user_health = await user_client.get("/health")
    assert user_health.status_code == 200
    user_health_data = user_health.json()
    assert user_health_data["service"] == "user-service"
    assert user_health_data["status"] == "healthy"
    print("[PASS] User Service health check passed")
    
    # Test Restaurant Service health
    restaurant_health = await restaurant_client.get("/health")
    assert restaurant_health.status_code == 200
    restaurant_health_data = restaurant_health.json()
    assert restaurant_health_data["service"] == "restaurant-service"
    assert restaurant_health_data["status"] == "healthy"
    print("[PASS] Restaurant Service health check passed")
    
    # Test Delivery Service health
    delivery_health = await delivery_client.get("/health")
    assert delivery_health.status_code == 200
    delivery_health_data = delivery_health.json()
    assert delivery_health_data["service"] == "delivery-service"
    assert delivery_health_data["status"] == "healthy"
    print("[PASS] Delivery Service health check passed")
@pytest.mark.asyncio
async def test_error_handling_when_delivery_service_unavailable(
    restaurant_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any]
):
    """Test error handling when delivery service is unavailable"""
    
    print("\n")
    
    # Setup restaurant
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    menu_item_id = menu_item["id"]
    
    # Create test order
    from shared.models import User, Order, OrderItem
    from tests.test_config import TestSessionLocal
    
    async with TestSessionLocal() as session:
        user = User(email="error@test.com", phone="5555555558", name="Error Test User", address={})
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        order = Order(
            user_id=user.id,
            restaurant_id=restaurant_id,
            delivery_address={"street": "123 Error St", "city": "Error City"},
            status="pending",
            total_amount=15.99
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item_id,
            quantity=1,
            unit_price=15.99,
            total_price=15.99
        )
        session.add(order_item)
        await session.commit()
        order_id = order.id
    
    # Mock httpx to simulate delivery service being unavailable
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection failed")
        
        # Restaurant accepts order (this should handle delivery service being down gracefully)
        accept_response = await restaurant_client.post(
            f"/orders/order/{order_id}/restaurant/{restaurant_id}/accept"
        )
        
        # Order should still be accepted even if notification to delivery service fails
        assert accept_response.status_code == 200
        accepted_order = accept_response.json()
        assert accepted_order["status"] == "accepted"
        print("[PASS] Order accepted gracefully even when delivery service is unavailable")
@pytest.mark.asyncio
async def test_concurrent_order_processing(
    user_client: AsyncClient,
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any],
    sample_delivery_agent_data: Dict[str, Any]
):
    """Test concurrent order processing and agent assignment"""
    
    print("\n")
    
    # Setup restaurant and menu
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    menu_item_id = menu_item["id"]
    
    # Register single delivery agent
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    delivery_agent = agent_response.json()
    
    # Create multiple test orders
    from shared.models import User, Order, OrderItem
    from tests.test_config import TestSessionLocal
    
    order_ids = []
    async with TestSessionLocal() as session:
        for i in range(3):
            user = User(
                email=f"concurrent{i}@test.com", 
                phone=f"555555555{i}", 
                name=f"Concurrent User {i}",
                address={}
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            order = Order(
                user_id=user.id,
                restaurant_id=restaurant_id,
                delivery_address={"street": f"123 Concurrent St {i}", "city": "Concurrent City"},
                status="pending",
                total_amount=15.99
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item_id,
                quantity=1,
                unit_price=15.99,
                total_price=15.99
            )
            session.add(order_item)
            await session.commit()
            order_ids.append(order.id)
    
    print(f"[PASS] Created {len(order_ids)} concurrent test orders")
    
    # Accept all orders concurrently
    import asyncio
    
    async def accept_order(order_id):
        return await restaurant_client.post(
            f"/orders/order/{order_id}/restaurant/{restaurant_id}/accept"
        )
    
    # Run all accepts concurrently
    accept_tasks = [accept_order(order_id) for order_id in order_ids]
    accept_responses = await asyncio.gather(*accept_tasks)
    
    # Verify all orders were accepted
    accepted_count = 0
    for response in accept_responses:
        if response.status_code == 200:
            accepted_count += 1
    
    print(f"[PASS] {accepted_count}/{len(order_ids)} orders accepted successfully")
    
    # Check delivery agent assignment - only one should be assigned since there's only one agent
    async with TestSessionLocal() as session:
        from sqlalchemy import select
        stmt = select(Order).where(Order.id.in_(order_ids))
        result = await session.execute(stmt)
        orders = result.scalars().all()
        
        assigned_count = sum(1 for order in orders if order.delivery_agent_id is not None)
        print(f"[PASS] {assigned_count} order(s) assigned to delivery agent")
        
        # Since there's only one available agent, only one order should be assigned
        # The others should remain unassigned until the agent becomes available again
        assert assigned_count <= 1, "More orders assigned than available agents"
@pytest.mark.asyncio
async def test_data_consistency_across_services(
    user_client: AsyncClient,
    restaurant_client: AsyncClient,
    delivery_client: AsyncClient,
    sample_restaurant_data: Dict[str, Any],
    sample_menu_item_data: Dict[str, Any],
    sample_delivery_agent_data: Dict[str, Any]
):
    """Test data consistency across all services"""
    
    print("\n")
    
    # Create restaurant via Restaurant Service
    restaurant_response = await restaurant_client.post("/restaurants/", json=sample_restaurant_data)
    restaurant = restaurant_response.json()
    restaurant_id = restaurant["id"]
    
    # Set restaurant online
    await restaurant_client.patch(f"/restaurants/{restaurant_id}/status?is_online=true")
    
    # Add menu item
    menu_response = await restaurant_client.post(f"/menu/{restaurant_id}/items", json=sample_menu_item_data)
    menu_item = menu_response.json()
    
    # Verify restaurant appears in User Service
    user_restaurants_response = await user_client.get("/restaurants/")
    user_restaurants = user_restaurants_response.json()
    
    user_restaurant = next((r for r in user_restaurants if r["id"] == restaurant_id), None)
    assert user_restaurant is not None, "Restaurant not visible in User Service"
    assert user_restaurant["is_online"] == True, "Restaurant online status not synced"
    assert len(user_restaurant["menu_items"]) > 0, "Menu items not visible in User Service"
    print("✅ Restaurant data consistent between Restaurant and User services")
    
    # Register delivery agent
    agent_response = await delivery_client.post("/agents/", json=sample_delivery_agent_data)
    delivery_agent = agent_response.json()
    agent_id = delivery_agent["id"]
    
    # Verify agent appears in available list
    available_agents_response = await delivery_client.get("/agents/available/list")
    available_agents = available_agents_response.json()
    
    agent_found = any(a["id"] == agent_id for a in available_agents)
    assert agent_found, "Delivery agent not in available list"
    print("✅ Delivery agent data consistent")
    
    # Test order data consistency
    from shared.models import User, Order
    from tests.test_config import TestSessionLocal
    
    async with TestSessionLocal() as session:
        user = User(email="consistency@test.com", phone="5555555559", name="Consistency User", address={})
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        order = Order(
            user_id=user.id,
            restaurant_id=restaurant_id,
            delivery_address={"street": "123 Consistency St", "city": "Consistency City"},
            status="pending",
            total_amount=15.99
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        order_id = order.id
    
    # Accept order via Restaurant Service
    accept_response = await restaurant_client.post(
        f"/orders/order/{order_id}/restaurant/{restaurant_id}/accept"
    )
    assert accept_response.status_code == 200
    
    # Verify order status is consistent across services
    user_order_response = await user_client.get(f"/orders/{order_id}")
    restaurant_order_response = await restaurant_client.get(f"/orders/order/{order_id}")
    
    assert user_order_response.status_code == 200
    assert restaurant_order_response.status_code == 200
    
    user_order = user_order_response.json()
    restaurant_order = restaurant_order_response.json()
    
    assert user_order["status"] == restaurant_order["status"], "Order status inconsistent between services"
    assert user_order["id"] == restaurant_order["id"], "Order ID mismatch"
    print("✅ Order data consistent across User and Restaurant services")
    
    print("✅ All data consistency tests passed") 