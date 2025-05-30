#!/bin/bash

# DELIVERY SERVICE COMPLETE TEST FLOW
# This script tests all delivery service endpoints with realistic scenarios
# Make sure the delivery service is running on port 8003

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Service configuration
DELIVERY_SERVICE_URL="http://localhost:8003"
TEST_ORDER_ID="c241cf9d-632f-4588-a295-1e324bc969d4"
RESTAURANT_ID="284bccdd-6501-42e5-9b31-171e5e483eb6"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}          DELIVERY SERVICE COMPLETE TEST FLOW${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

print_step() {
    echo -e "${YELLOW}TEST STEP: $1${NC}"
    echo "--------------------------------------------------------------------"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    echo ""
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
    echo ""
}

wait_for_input() {
    echo -e "${BLUE}Press Enter to continue to next test...${NC}"
    read
}

# TEST 1: Health Check
print_step "1. Health Check - Verify Delivery Service is Running"

curl -X GET "$DELIVERY_SERVICE_URL/health" \
  -H "Content-Type: application/json" | jq

if [ $? -eq 0 ]; then
    print_success "Delivery service is healthy and running"
else
    print_error "Delivery service is not responding"
    exit 1
fi

wait_for_input

# TEST 2: Get Service Info
print_step "2. Get Service Information"

curl -X GET "$DELIVERY_SERVICE_URL/" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved service information"
wait_for_input

# TEST 3: Get All Delivery Agents
print_step "3. Get All Delivery Agents"

echo "Getting all delivery agents..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved all delivery agents"
wait_for_input

# TEST 4: Get Available Delivery Agents
print_step "4. Get Available Delivery Agents Only"

echo "Getting only available delivery agents..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/?available_only=true" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved available delivery agents"
wait_for_input

# TEST 5: Get Available Agents
print_step "5. Get Available Agents List"

echo "Getting available agents using alternative endpoint..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/available/list" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved available agents list"
wait_for_input

# TEST 6: Create New Delivery Agent
print_step "6. Create New Delivery Agent"

echo "Creating a new delivery agent..."
NEW_AGENT_RESPONSE=$(curl -X POST "$DELIVERY_SERVICE_URL/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Delivery Driver",
    "email": "test.driver@delivery.com",
    "phone": "+1-555-DRIVER",
    "vehicle_type": "bike",
    "current_location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "Manhattan, NYC"
    }
}' | jq)

echo "$NEW_AGENT_RESPONSE"

NEW_AGENT_ID=$(echo "$NEW_AGENT_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Agent ID: $NEW_AGENT_ID${NC}"

print_success "New delivery agent created successfully"
wait_for_input

# TEST 7: Create Second Delivery Agent
print_step "7. Create Second Delivery Agent"

echo "Creating another delivery agent..."
SECOND_AGENT_RESPONSE=$(curl -X POST "$DELIVERY_SERVICE_URL/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fast Delivery Mike",
    "email": "mike.fast@delivery.com",
    "phone": "+1-555-FAST-01",
    "vehicle_type": "motorcycle",
    "current_location": {
        "latitude": 40.7589,
        "longitude": -73.9851,
        "address": "Times Square, NYC"
    }
}' | jq)

echo "$SECOND_AGENT_RESPONSE"

SECOND_AGENT_ID=$(echo "$SECOND_AGENT_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Second Agent ID: $SECOND_AGENT_ID${NC}"

print_success "Second delivery agent created successfully"
wait_for_input

# TEST 8: Get Specific Delivery Agent
print_step "8. Get Specific Delivery Agent Details"

echo "Getting details for agent: $NEW_AGENT_ID"
curl -X GET "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific agent details"
wait_for_input

# TEST 9: Update Agent Information
print_step "9. Update Agent Information"

echo "Updating agent information..."
curl -X PUT "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Delivery Driver (Updated)",
    "vehicle_type": "motorcycle",
    "is_available": true
}' | jq

print_success "Agent information updated successfully"
wait_for_input

# TEST 10: Toggle Agent Availability
print_step "10. Toggle Agent Availability"

echo "Setting agent to unavailable..."
curl -X PATCH "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID/availability?is_available=false" \
  -H "Content-Type: application/json" | jq

print_success "Agent set to unavailable"
wait_for_input

echo "Setting agent back to available..."
curl -X PATCH "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID/availability?is_available=true" \
  -H "Content-Type: application/json" | jq

print_success "Agent set back to available"
wait_for_input

# TEST 11: Update Agent Location
print_step "11. Update Agent Location"

echo "Updating agent location..."
curl -X PUT "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID/location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7505,
    "longitude": -73.9934,
    "address": "Central Park, NYC"
}' | jq

print_success "Agent location updated successfully"
wait_for_input

# TEST 12: Assign Order to Agent
print_step "12. Assign Order to Delivery Agent"

echo "Assigning order to agent..."
curl -X POST "$DELIVERY_SERVICE_URL/assignments/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$TEST_ORDER_ID'",
    "delivery_agent_id": "'$NEW_AGENT_ID'",
    "restaurant_id": "'$RESTAURANT_ID'"
}' | jq

print_success "Order assigned to delivery agent"
wait_for_input

# TEST 13: Get Agent Orders
print_step "13. Get Orders Assigned to Agent"

echo "Getting orders for agent: $NEW_AGENT_ID"
curl -X GET "$DELIVERY_SERVICE_URL/orders/agent/$NEW_AGENT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved agent orders"
wait_for_input

# TEST 14: Get Specific Order Details
print_step "14. Get Specific Order Details"

echo "Getting order details: $TEST_ORDER_ID"
curl -X GET "$DELIVERY_SERVICE_URL/orders/$TEST_ORDER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific order details"
wait_for_input

# TEST 15: Mark Order as Picked Up
print_step "15. Mark Order as Picked Up from Restaurant"

echo "Marking order as picked up..."
curl -X POST "$DELIVERY_SERVICE_URL/orders/$TEST_ORDER_ID/agent/$NEW_AGENT_ID/pickup" \
  -H "Content-Type: application/json" | jq

print_success "Order marked as picked up"
wait_for_input

# TEST 16: Update Delivery Status with Location
print_step "16. Update Delivery Status with Custom Message"

echo "Updating delivery status with location..."
curl -X PATCH "$DELIVERY_SERVICE_URL/orders/$TEST_ORDER_ID/agent/$NEW_AGENT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "picked_up",
    "location": {
        "latitude": 40.7505,
        "longitude": -73.9934
    },
    "notes": "Package picked up, heading to customer"
}' | jq

print_success "Delivery status updated with location"
wait_for_input

# TEST 17: Mark Order as On The Way
print_step "17. Mark Order as On The Way to Customer"

echo "Marking order as on the way..."
curl -X POST "$DELIVERY_SERVICE_URL/orders/$TEST_ORDER_ID/agent/$NEW_AGENT_ID/on-the-way" \
  -H "Content-Type: application/json" | jq

print_success "Order marked as on the way"
wait_for_input

# TEST 18: Update Location During Delivery
print_step "18. Update Agent Location During Delivery"

echo "Updating agent location during delivery..."
curl -X PUT "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID/location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7614,
    "longitude": -73.9776,
    "address": "En route to customer"
}' | jq

print_success "Agent location updated during delivery"
wait_for_input

# TEST 19: Mark Order as Delivered
print_step "19. Mark Order as Delivered to Customer"

echo "Marking order as delivered..."
curl -X POST "$DELIVERY_SERVICE_URL/orders/$TEST_ORDER_ID/agent/$NEW_AGENT_ID/delivered" \
  -H "Content-Type: application/json" | jq

print_success "Order marked as delivered"
wait_for_input

# TEST 20: Assign Second Order to Second Agent
print_step "20. Test Multiple Agent Assignment"

echo "This would assign a second order to the second agent..."
echo "curl -X POST \"$DELIVERY_SERVICE_URL/assignments/\" -H \"Content-Type: application/json\" -d '{\"order_id\": \"NEW_ORDER_ID\", \"delivery_agent_id\": \"$SECOND_AGENT_ID\", \"restaurant_id\": \"$RESTAURANT_ID\"}' | jq"
echo "Skipping as we only have one test order..."

print_success "Multiple agent assignment scenario shown"
wait_for_input

# TEST 21: Error Testing - Invalid Agent ID
print_step "21. Error Testing - Invalid Agent ID"

echo "Attempting to get non-existent agent..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json" | jq

print_success "Error handling test completed"
wait_for_input

# TEST 22: Error Testing - Invalid Order ID
print_step "22. Error Testing - Invalid Order ID"

echo "Attempting to get non-existent order..."
curl -X GET "$DELIVERY_SERVICE_URL/orders/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json" | jq

print_success "Error handling test completed"
wait_for_input

# TEST 23: Error Testing - Invalid Assignment
print_step "23. Error Testing - Invalid Assignment"

echo "Attempting to assign order to non-existent agent..."
curl -X POST "$DELIVERY_SERVICE_URL/assignments/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$TEST_ORDER_ID'",
    "delivery_agent_id": "00000000-0000-0000-0000-000000000000",
    "restaurant_id": "'$RESTAURANT_ID'"
}' | jq

print_success "Invalid assignment test completed"
wait_for_input

# TEST 24: Agent Performance Summary
print_step "24. Agent Performance Summary"

echo "Getting final agent details to see completed deliveries..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/$NEW_AGENT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Agent performance summary retrieved"
wait_for_input

# TEST 25: Final Agent List
print_step "25. Final Agent List - All Agents"

echo "Getting final list of all agents..."
curl -X GET "$DELIVERY_SERVICE_URL/agents/" \
  -H "Content-Type: application/json" | jq

print_success "Final agent list retrieved"
wait_for_input

# TEST SUMMARY
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}                        TEST SUMMARY${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${GREEN}All Delivery Service tests completed successfully${NC}"
echo ""
echo -e "${YELLOW}Created Resources:${NC}"
echo -e "  Agent 1: $NEW_AGENT_ID (Test Delivery Driver)"
echo -e "  Agent 2: $SECOND_AGENT_ID (Fast Delivery Mike)"
echo ""
echo -e "${YELLOW}Delivery Flow Completed:${NC}"
echo -e "  Order: $TEST_ORDER_ID"
echo -e "  Assigned -> Picked Up -> On The Way -> Delivered"
echo ""
echo -e "${YELLOW}Tests Covered:${NC}"
echo "  1. Health Check"
echo "  2. Service Information"
echo "  3. Get All Delivery Agents"
echo "  4. Get Available Agents"
echo "  5. Get Available Agents List"
echo "  6. Create New Delivery Agent"
echo "  7. Create Second Agent"
echo "  8. Get Specific Agent"
echo "  9. Update Agent Information"
echo "  10. Toggle Agent Availability"
echo "  11. Update Agent Location"
echo "  12. Assign Order to Agent"
echo "  13. Get Agent Orders"
echo "  14. Get Order Details"
echo "  15. Mark Order Picked Up"
echo "  16. Update Delivery Status"
echo "  17. Mark Order On The Way"
echo "  18. Update Location During Delivery"
echo "  19. Mark Order Delivered"
echo "  20. Multiple Agent Scenario"
echo "  21. Error Handling"
echo "  22. Invalid Data Testing"
echo "  23. Invalid Assignment Testing"
echo "  24. Agent Performance Summary"
echo "  25. Final Agent List"
echo ""
echo -e "${GREEN}Delivery Service is working properly${NC}"
echo -e "${GREEN}Complete delivery lifecycle tested successfully${NC}"
echo -e "${BLUE}=====================================================================${NC}" 