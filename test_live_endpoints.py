#!/usr/bin/env python3
"""
Comprehensive Live Endpoint Testing for Food Delivery Microservices
Tests all endpoints with actual JSON inputs against running services
"""

import asyncio
import json
import httpx
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

# Service endpoints
SERVICES = {
    "user": "http://localhost:8001",
    "restaurant": "http://localhost:8002", 
    "delivery": "http://localhost:8003"
}

# Generate unique identifiers for this test run
TEST_RUN_ID = int(time.time())
UNIQUE_SUFFIX = f"_{TEST_RUN_ID}"

# Test data with unique emails
SAMPLE_RESTAURANT_DATA = {
    "name": f"Test Pizza Palace {TEST_RUN_ID}",
    "phone": "+1234567890",
    "email": f"pizza{UNIQUE_SUFFIX}@testpalace.com",
    "address": {
        "street": "123 Pizza St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "USA"
    },
    "cuisine_type": "Italian",
    "description": "Best pizza in town!",
    "is_online": True
}

SAMPLE_MENU_ITEM_DATA = {
    "name": "Margherita Pizza",
    "description": "Classic pizza with tomato sauce, mozzarella, and basil",
    "price": 15.99,
    "category": "Pizza",
    "is_vegetarian": True,
    "is_available": True,
    "preparation_time": 20
}

SAMPLE_DELIVERY_AGENT_DATA = {
    "name": f"John Delivery {TEST_RUN_ID}",
    "phone": "+1987654321",
    "email": f"john.delivery{UNIQUE_SUFFIX}@test.com",
    "vehicle_type": "motorcycle",
    "is_available": True,
    "current_location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "New York, NY"
    }
}

SAMPLE_USER_DATA = {
    "name": "Test User",
    "email": "testuser@example.com",
    "phone": "+1555123456",
    "address": {
        "street": "456 User St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "USA"
    }
}

class EndpointTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_data = {}
        self.pass_count = 0
        self.fail_count = 0
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def is_success_status(self, status_code: int) -> bool:
        """Check if status code indicates success (2xx range)"""
        return 200 <= status_code < 300

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result and keep count"""
        if passed:
            self.pass_count += 1
            print(f"[PASS] {test_name}")
            if details:
                print(f"       {details}")
        else:
            self.fail_count += 1
            print(f"[FAIL] {test_name}")
            if details:
                print(f"       {details}")

    async def test_service_health(self) -> bool:
        """Test health endpoints for all services"""
        print("\n")
        
        all_healthy = True
        for service_name, base_url in SERVICES.items():
            try:
                response = await self.client.get(f"{base_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_result(f"{service_name.upper()} Service Health", True, str(health_data))
                else:
                    self.log_result(f"{service_name.upper()} Service Health", False, f"Status {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_result(f"{service_name.upper()} Service Health", False, str(e))
                all_healthy = False
                
        return all_healthy

    async def test_restaurant_endpoints(self) -> Dict[str, Any]:
        """Test all Restaurant Service endpoints with JSON data"""
        print("\n")
        
        base_url = SERVICES["restaurant"]
        results = {}
        
        Register Restaurant
        print("\n1. Testing Restaurant Registration...")
        restaurant_data = SAMPLE_RESTAURANT_DATA.copy()
        response = await self.client.post(f"{base_url}/restaurants/", json=restaurant_data)
        
        if self.is_success_status(response.status_code):
            restaurant = response.json()
            restaurant_id = restaurant["id"]
            results["restaurant_id"] = restaurant_id
            self.log_result("Restaurant Registration", True, 
                          f"Restaurant: {restaurant['name']} (ID: {restaurant_id}), Status: {response.status_code}")
            print(f"       JSON Response: {json.dumps(restaurant, indent=2)}")
        else:
            self.log_result("Restaurant Registration", False, 
                          f"Status: {response.status_code}, Error: {response.text}")
            print(f"[INFO] Service docs available at: {base_url}/docs")
            return results

        Get Restaurant Details
        print("\n2. Testing Get Restaurant Details...")
        response = await self.client.get(f"{base_url}/restaurants/{restaurant_id}")
        if self.is_success_status(response.status_code):
            restaurant_details = response.json()
            self.log_result("Get Restaurant Details", True, "Restaurant details retrieved")
            print(f"       JSON Response: {json.dumps(restaurant_details, indent=2)}")
        else:
            self.log_result("Get Restaurant Details", False, f"Status: {response.status_code}")

        List All Restaurants
        print("\n3. Testing List All Restaurants...")
        response = await self.client.get(f"{base_url}/restaurants/")
        if self.is_success_status(response.status_code):
            restaurants = response.json()
            self.log_result("List All Restaurants", True, f"Retrieved {len(restaurants)} restaurants")
            if restaurants:
                print(f"       JSON Response: {json.dumps(restaurants[:1], indent=2)}...")
        else:
            self.log_result("List All Restaurants", False, f"Status: {response.status_code}")

        Update Restaurant Status
        print("\n4. Testing Update Restaurant Status...")
        response = await self.client.patch(f"{base_url}/restaurants/{restaurant_id}/status?is_online=true")
        if self.is_success_status(response.status_code):
            updated_restaurant = response.json()
            self.log_result("Update Restaurant Status", True, f"Restaurant status updated: Online = {updated_restaurant['is_online']}")
            print(f"       JSON Response: {json.dumps(updated_restaurant, indent=2)}")
        else:
            self.log_result("Update Restaurant Status", False, f"Status: {response.status_code}")

        Add Menu Item
        print("\n5. Testing Add Menu Item...")
        menu_item_data = SAMPLE_MENU_ITEM_DATA.copy()
        response = await self.client.post(f"{base_url}/menu/{restaurant_id}/items", json=menu_item_data)
        
        if self.is_success_status(response.status_code):
            menu_item = response.json()
            menu_item_id = menu_item["id"]
            results["menu_item_id"] = menu_item_id
            self.log_result("Add Menu Item", True, f"Menu item added: {menu_item['name']} (ID: {menu_item_id})")
            print(f"       JSON Response: {json.dumps(menu_item, indent=2)}")
        else:
            self.log_result("Add Menu Item", False, f"Status: {response.status_code}, Error: {response.text}")

        Get Restaurant Menu
        print("\n6. Testing Get Restaurant Menu...")
        response = await self.client.get(f"{base_url}/menu/{restaurant_id}/items")
        if self.is_success_status(response.status_code):
            menu_items = response.json()
            self.log_result("Get Restaurant Menu", True, f"Retrieved {len(menu_items)} menu items")
            print(f"       JSON Response: {json.dumps(menu_items, indent=2)}")
        else:
            self.log_result("Get Restaurant Menu", False, f"Status: {response.status_code}")

        Update Menu Item
        if "menu_item_id" in results:
            print("\n7. Testing Update Menu Item...")
            update_data = {"price": 17.99, "description": "Updated delicious pizza"}
            response = await self.client.put(f"{base_url}/menu/items/{results['menu_item_id']}", json=update_data)
            if self.is_success_status(response.status_code):
                updated_item = response.json()
                self.log_result("Update Menu Item", True, f"Menu item updated: Price = ${updated_item['price']}")
                print(f"       JSON Response: {json.dumps(updated_item, indent=2)}")
            else:
                self.log_result("Update Menu Item", False, f"Status: {response.status_code}")

        Toggle Menu Item Availability
        if "menu_item_id" in results:
            print("\n8. Testing Toggle Menu Item Availability...")
            response = await self.client.patch(f"{base_url}/menu/items/{results['menu_item_id']}/availability?is_available=false")
            if self.is_success_status(response.status_code):
                updated_item = response.json()
                self.log_result("Toggle Menu Item Availability", True, f"Menu item availability toggled: Available = {updated_item['is_available']}")
                print(f"       JSON Response: {json.dumps(updated_item, indent=2)}")
            else:
                self.log_result("Toggle Menu Item Availability", False, f"Status: {response.status_code}")

        return results

    async def test_delivery_endpoints(self) -> Dict[str, Any]:
        """Test all Delivery Service endpoints with JSON data"""
        print("\n")
        
        base_url = SERVICES["delivery"]
        results = {}
        
        Register Delivery Agent
        print("\n1. Testing Delivery Agent Registration...")
        agent_data = SAMPLE_DELIVERY_AGENT_DATA.copy()
        response = await self.client.post(f"{base_url}/agents/", json=agent_data)
        
        if self.is_success_status(response.status_code):
            agent = response.json()
            agent_id = agent["id"]
            results["agent_id"] = agent_id
            self.log_result("Delivery Agent Registration", True, 
                          f"Agent: {agent['name']} (ID: {agent_id}), Status: {response.status_code}")
            print(f"       JSON Response: {json.dumps(agent, indent=2)}")
        else:
            self.log_result("Delivery Agent Registration", False, 
                          f"Status: {response.status_code}, Error: {response.text}")
            return results

        Get Agent Details
        print("\n2. Testing Get Agent Details...")
        response = await self.client.get(f"{base_url}/agents/{agent_id}")
        if self.is_success_status(response.status_code):
            agent_details = response.json()
            self.log_result("Get Agent Details", True, "Agent details retrieved successfully")
            print(f"       JSON Response: {json.dumps(agent_details, indent=2)}")
        else:
            self.log_result("Get Agent Details", False, f"Status: {response.status_code}")

        List All Agents
        print("\n3. Testing List All Agents...")
        response = await self.client.get(f"{base_url}/agents/")
        if self.is_success_status(response.status_code):
            agents = response.json()
            self.log_result("List All Agents", True, f"Retrieved {len(agents)} agents")
            if agents:
                print(f"       JSON Response: {json.dumps(agents[:1], indent=2)}...")
        else:
            self.log_result("List All Agents", False, f"Status: {response.status_code}")

        Get Available Agents
        print("\n4. Testing Get Available Agents...")
        response = await self.client.get(f"{base_url}/agents/available/list")
        if self.is_success_status(response.status_code):
            available_agents = response.json()
            self.log_result("Get Available Agents", True, f"Found {len(available_agents)} available agents")
            print(f"       JSON Response: {json.dumps(available_agents, indent=2)}")
        else:
            self.log_result("Get Available Agents", False, f"Status: {response.status_code}")

        Update Agent Availability
        print("\n5. Testing Update Agent Availability...")
        response = await self.client.patch(f"{base_url}/agents/{agent_id}/availability?is_available=false")
        if self.is_success_status(response.status_code):
            updated_agent = response.json()
            self.log_result("Update Agent Availability", True, f"Available: {updated_agent['is_available']}")
            print(f"       JSON Response: {json.dumps(updated_agent, indent=2)}")
        else:
            self.log_result("Update Agent Availability", False, f"Status: {response.status_code}")

        Update Agent Location
        print("\n6. Testing Update Agent Location...")
        location_data = {
            "latitude": 40.7589,
            "longitude": -73.9851,
            "address": "Times Square, NY"
        }
        response = await self.client.put(f"{base_url}/agents/{agent_id}/location", json=location_data)
        if self.is_success_status(response.status_code):
            updated_agent = response.json()
            self.log_result("Update Agent Location", True, "Location updated successfully")
            print(f"       JSON Response: {json.dumps(updated_agent, indent=2)}")
        else:
            self.log_result("Update Agent Location", False, f"Status: {response.status_code}")

        Get Agent Assignments
        print("\n7. Testing Get Agent Assignments...")
        response = await self.client.get(f"{base_url}/assignments/{agent_id}")
        if self.is_success_status(response.status_code):
            assignments = response.json()
            self.log_result("Get Agent Assignments", True, f"Retrieved {len(assignments)} assignments")
            print(f"       JSON Response: {json.dumps(assignments, indent=2)}")
        else:
            self.log_result("Get Agent Assignments", False, f"Status: {response.status_code}")

        return results

    async def test_user_endpoints(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test all User Service endpoints with JSON data"""
        print("\n")
        
        base_url = SERVICES["user"]
        results = {}
        
        List Online Restaurants
        print("\n1. Testing List Online Restaurants...")
        response = await self.client.get(f"{base_url}/restaurants/")
        if self.is_success_status(response.status_code):
            restaurants = response.json()
            self.log_result("List Online Restaurants", True, f"Listed {len(restaurants)} online restaurants")
            if restaurants:
                print(f"       JSON Response: {json.dumps(restaurants[0], indent=2)}...")
        else:
            self.log_result("List Online Restaurants", False, 
                          f"Status: {response.status_code}, Error: {response.text}")

        Get Restaurant Details with Menu
        if restaurant_data.get("restaurant_id"):
            restaurant_id = restaurant_data["restaurant_id"]
            print(f"\n2. Testing Get Restaurant Details with Menu (ID: {restaurant_id})...")
            response = await self.client.get(f"{base_url}/restaurants/{restaurant_id}")
            if self.is_success_status(response.status_code):
                restaurant_details = response.json()
                self.log_result("Get Restaurant Details with Menu", True, "Restaurant details with menu retrieved")
                print(f"       JSON Response: {json.dumps(restaurant_details, indent=2)}")
            else:
                self.log_result("Get Restaurant Details with Menu", False, f"Status: {response.status_code}")

        return results

    async def test_simple_endpoints(self):
        """Test simple endpoints to understand what's working"""
        print("\n")
        
        for service_name, base_url in SERVICES.items():
            print(f"\nTesting {service_name.upper()} Service:")
            
            # Test OpenAPI docs
            try:
                response = await self.client.get(f"{base_url}/docs")
                if response.status_code == 200:
                    self.log_result(f"{service_name.upper()} Service Docs", True, "Docs available at {base_url}/docs")
                else:
                    self.log_result(f"{service_name.upper()} Service Docs", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"{service_name.upper()} Service Docs", False, f"Not accessible: {e}")
            
            # Test root endpoint
            try:
                response = await self.client.get(f"{base_url}/")
                self.log_result(f"{service_name.upper()} Service Root", True, f"Root endpoint status: {response.status_code}")
                if self.is_success_status(response.status_code):
                    self.log_result(f"{service_name.upper()} Service Root", True, f"         Response: {response.text}")
            except Exception as e:
                self.log_result(f"{service_name.upper()} Service Root", False, f"Root endpoint error: {e}")

async def main():
    """Run comprehensive endpoint testing"""
    print("Starting Comprehensive Food Delivery API Testing")
    print("=" * 60)
    
    async with EndpointTester() as tester:
        Test service health
        if not await tester.test_service_health():
            print("\nSome services are not healthy. Please check service status.")
            return
            
        Test simple endpoints first
        await tester.test_simple_endpoints()
        
        Test Delivery Service endpoints first (known to work)
        delivery_results = await tester.test_delivery_endpoints()
        
        Test Restaurant Service endpoints
        restaurant_results = await tester.test_restaurant_endpoints()
        
        Test User Service endpoints
        user_results = await tester.test_user_endpoints(restaurant_results)
        
        print("\n" + "=" * 60)
        print("Comprehensive API Testing Complete!")
        print("\nTest Results Summary:")
        print(f"   • Total Tests Passed: {tester.pass_count}")
        print(f"   • Total Tests Failed: {tester.fail_count}")
        print(f"   • Success Rate: {tester.pass_count/(tester.pass_count + tester.fail_count)*100:.1f}%")
        print(f"   • Delivery Service: {len(delivery_results)} core objects created")
        print(f"   • Restaurant Service: {len(restaurant_results)} core objects created") 
        print(f"   • User Service: {len(user_results)} core objects created")
        print("\nTesting completed with actual JSON data and comprehensive results!")

if __name__ == "__main__":
    asyncio.run(main()) 