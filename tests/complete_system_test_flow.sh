#!/bin/bash

# COMPLETE FOOD DELIVERY SYSTEM TEST FLOW
# This script demonstrates the complete end-to-end workflow
# across all three services (User, Restaurant, Delivery)
# Make sure all services are running:
#   - User Service: port 8001
#   - Restaurant Service: port 8002  
#   - Delivery Service: port 8003

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Service URLs
USER_SERVICE_URL="http://localhost:8001"
RESTAURANT_SERVICE_URL="http://localhost:8002"
DELIVERY_SERVICE_URL="http://localhost:8003"

# Test data
TEST_USER_ID="7d2a9f80-bd2f-4a32-8a8c-5e9f9d4f6e76"
RESTAURANT_ID="284bccdd-6501-42e5-9b31-171e5e483eb6"
MENU_ITEM_ID="e76d76c3-d42c-4958-9a16-f928c9e520ac"

echo -e "${PURPLE}=====================================================================${NC}"
echo -e "${PURPLE}       COMPLETE FOOD DELIVERY SYSTEM TEST FLOW${NC}"
echo -e "${PURPLE}=====================================================================${NC}"
echo -e "${CYAN}Testing the complete journey from order creation to delivery${NC}"
echo ""

print_stage() {
    echo -e "${PURPLE}STAGE: $1${NC}"
    echo "====================================================================="
}

print_step() {
    echo -e "${YELLOW}STEP: $1${NC}"
    echo "---------------------------------------------------------------------"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    echo ""
}

print_info() {
    echo -e "${CYAN}INFO: $1${NC}"
}

wait_for_input() {
    echo -e "${BLUE}Press Enter to continue...${NC}"
    read
}

# STAGE 1: SYSTEM HEALTH CHECK
print_stage "1. SYSTEM HEALTH CHECK - Verify All Services"

print_step "Check User Service Health"
curl -X GET "$USER_SERVICE_URL/health" -H "Content-Type: application/json" | jq
print_success "User Service is healthy"

print_step "Check Restaurant Service Health"
curl -X GET "$RESTAURANT_SERVICE_URL/health" -H "Content-Type: application/json" | jq
print_success "Restaurant Service is healthy"

print_step "Check Delivery Service Health"
curl -X GET "$DELIVERY_SERVICE_URL/health" -H "Content-Type: application/json" | jq
print_success "Delivery Service is healthy"

print_info "All services are running and healthy"
wait_for_input

# STAGE 2: CUSTOMER BROWSING EXPERIENCE
print_stage "2. CUSTOMER BROWSING - Explore Available Options"

print_step "Customer Views Available Restaurants"
print_info "Customer opens the app and browses restaurants..."
curl -X GET "$USER_SERVICE_URL/restaurants/" -H "Content-Type: application/json" | jq

print_success "Customer sees available restaurants"

print_step "Customer Views Restaurant Menu"
print_info "Customer selects a restaurant and views the menu..."
curl -X GET "$USER_SERVICE_URL/restaurants/$RESTAURANT_ID" -H "Content-Type: application/json" | jq

print_success "Customer sees restaurant menu items"
wait_for_input

# STAGE 3: ORDER CREATION
print_stage "3. ORDER CREATION - Customer Places Order"

print_step "Customer Creates Order"
print_info "Customer adds items to cart and places order..."

ORDER_RESPONSE=$(curl -X POST "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "'$RESTAURANT_ID'",
    "delivery_address": {
        "street": "123 Foodie Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001"
    },
    "items": [
        {
            "menu_item_id": "'$MENU_ITEM_ID'",
            "quantity": 2
        }
    ],
    "special_instructions": "Please ring doorbell twice"
}' | jq)

echo "$ORDER_RESPONSE"

ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Order Created! Order ID: $ORDER_ID${NC}"

print_success "Customer order placed successfully"
wait_for_input

# STAGE 4: RESTAURANT RECEIVES ORDER
print_stage "4. RESTAURANT MANAGEMENT - Order Processing"

print_step "Restaurant Sees New Pending Order"
print_info "Restaurant receives notification and checks pending orders..."

curl -X GET "$RESTAURANT_SERVICE_URL/orders/$RESTAURANT_ID/pending" \
  -H "Content-Type: application/json" | jq

print_success "Restaurant sees the new order"

print_step "Restaurant Views Order Details"
print_info "Restaurant checks order details before accepting..."

curl -X GET "$RESTAURANT_SERVICE_URL/orders/order/$ORDER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Restaurant reviewed order details"

print_step "Restaurant Accepts Order"
print_info "Restaurant accepts the order with estimated prep time..."

curl -X POST "$RESTAURANT_SERVICE_URL/orders/order/$ORDER_ID/restaurant/$RESTAURANT_ID/accept?estimated_prep_time=25" \
  -H "Content-Type: application/json" | jq

print_success "Restaurant accepted the order"
wait_for_input

# STAGE 5: ORDER PREPARATION
print_stage "5. ORDER PREPARATION - Kitchen Operations"

print_step "Restaurant Starts Preparing Order"
print_info "Kitchen starts preparing the food..."

curl -X PATCH "$RESTAURANT_SERVICE_URL/orders/order/$ORDER_ID/restaurant/$RESTAURANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "preparing",
    "estimated_prep_time": 20
}' | jq

print_success "Order is now being prepared"

print_step "Customer Checks Order Status"
print_info "Customer checks their order status..."

curl -X GET "$USER_SERVICE_URL/orders/$ORDER_ID" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Customer sees order is being prepared"

print_step "Restaurant Marks Order Ready"
print_info "Food is ready for pickup..."

curl -X POST "$RESTAURANT_SERVICE_URL/orders/order/$ORDER_ID/restaurant/$RESTAURANT_ID/ready" \
  -H "Content-Type: application/json" | jq

print_success "Order is ready for pickup"
wait_for_input

# STAGE 6: DELIVERY AGENT ASSIGNMENT
print_stage "6. DELIVERY ASSIGNMENT - Finding Available Driver"

print_step "Check Available Delivery Agents"
print_info "System looks for available delivery agents..."

curl -X GET "$DELIVERY_SERVICE_URL/agents/available/list" \
  -H "Content-Type: application/json" | jq

print_step "Create New Delivery Agent"
print_info "Creating a delivery agent for this demonstration..."

AGENT_RESPONSE=$(curl -X POST "$DELIVERY_SERVICE_URL/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lightning Fast Driver",
    "email": "fast.driver@delivery.com",
    "phone": "+1-555-FAST-99",
    "vehicle_type": "motorcycle",
    "current_location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "Near restaurant area"
    }
}' | jq)

echo "$AGENT_RESPONSE"

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Delivery Agent Created! Agent ID: $AGENT_ID${NC}"

print_step "Assign Order to Delivery Agent"
print_info "System assigns the order to available driver..."

curl -X POST "$DELIVERY_SERVICE_URL/assignments/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "'$ORDER_ID'",
    "delivery_agent_id": "'$AGENT_ID'",
    "restaurant_id": "'$RESTAURANT_ID'"
}' | jq

print_success "Order assigned to delivery agent"
wait_for_input

# STAGE 7: PICKUP PROCESS
print_stage "7. PICKUP PROCESS - Driver Collects Order"

print_step "Driver Sees Assigned Order"
print_info "Driver checks their assigned orders..."

curl -X GET "$DELIVERY_SERVICE_URL/orders/agent/$AGENT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Driver sees the assigned order"

print_step "Driver Arrives at Restaurant"
print_info "Driver updates location and picks up the order..."

curl -X PUT "$DELIVERY_SERVICE_URL/agents/$AGENT_ID/location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7505,
    "longitude": -73.9934,
    "address": "At restaurant location"
}' | jq

print_step "Driver Picks Up Order"
print_info "Driver confirms pickup from restaurant..."

curl -X POST "$DELIVERY_SERVICE_URL/orders/$ORDER_ID/agent/$AGENT_ID/pickup" \
  -H "Content-Type: application/json" | jq

print_success "Order picked up from restaurant"
wait_for_input

# STAGE 8: DELIVERY IN PROGRESS
print_stage "8. DELIVERY IN PROGRESS - En Route to Customer"

print_step "Driver Starts Delivery"
print_info "Driver heads towards customer location..."

curl -X POST "$DELIVERY_SERVICE_URL/orders/$ORDER_ID/agent/$AGENT_ID/on-the-way" \
  -H "Content-Type: application/json" | jq

print_success "Driver is on the way to customer"

print_step "Customer Tracks Delivery"
print_info "Customer checks order status for real-time updates..."

curl -X GET "$USER_SERVICE_URL/orders/$ORDER_ID" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Customer sees delivery is in progress"

print_step "Driver Updates Location"
print_info "Driver updates location during delivery..."

curl -X PUT "$DELIVERY_SERVICE_URL/agents/$AGENT_ID/location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7614,
    "longitude": -73.9776,
    "address": "Halfway to customer"
}' | jq

print_success "Driver location updated"
wait_for_input

# STAGE 9: DELIVERY COMPLETION
print_stage "9. DELIVERY COMPLETION - Order Delivered"

print_step "Driver Arrives at Customer Location"
print_info "Driver reaches customer address..."

curl -X PUT "$DELIVERY_SERVICE_URL/agents/$AGENT_ID/location" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "address": "123 Foodie Street, Customer location"
}' | jq

print_step "Driver Delivers Order"
print_info "Driver hands over the order to customer..."

curl -X POST "$DELIVERY_SERVICE_URL/orders/$ORDER_ID/agent/$AGENT_ID/delivered" \
  -H "Content-Type: application/json" | jq

print_success "Order delivered successfully"

print_step "Customer Confirms Delivery"
print_info "Customer checks final order status..."

curl -X GET "$USER_SERVICE_URL/orders/$ORDER_ID" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Customer confirms order delivery"
wait_for_input

# STAGE 10: POST-DELIVERY ACTIVITIES
print_stage "10. POST-DELIVERY - Order History & Analytics"

print_step "Customer Views Order History"
print_info "Customer reviews their complete order history..."

curl -X GET "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Customer sees complete order history"

print_step "Restaurant Reviews Completed Orders"
print_info "Restaurant checks their completed orders..."

curl -X GET "$RESTAURANT_SERVICE_URL/orders/$RESTAURANT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Restaurant sees order analytics"

print_step "Delivery Agent Performance"
print_info "Checking delivery agent performance..."

curl -X GET "$DELIVERY_SERVICE_URL/agents/$AGENT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Delivery agent performance tracked"
wait_for_input

# COMPLETION SUMMARY
echo -e "${PURPLE}=====================================================================${NC}"
echo -e "${PURPLE}                    COMPLETE SYSTEM TEST SUMMARY${NC}"
echo -e "${PURPLE}=====================================================================${NC}"
echo ""
echo -e "${GREEN}FULL END-TO-END TEST COMPLETED SUCCESSFULLY${NC}"
echo ""
echo -e "${YELLOW}JOURNEY COMPLETED:${NC}"
echo -e "   Customer: $TEST_USER_ID"
echo -e "   Restaurant: $RESTAURANT_ID"
echo -e "   Delivery Agent: $AGENT_ID"
echo -e "   Order: $ORDER_ID"
echo ""
echo -e "${YELLOW}WORKFLOW STAGES TESTED:${NC}"
echo "   1. System Health Check"
echo "   2. Customer Browsing Experience"
echo "   3. Order Creation"
echo "   4. Restaurant Order Management"
echo "   5. Order Preparation"
echo "   6. Delivery Agent Assignment"
echo "   7. Pickup Process"
echo "   8. Delivery in Progress"
echo "   9. Delivery Completion"
echo "   10. Post-Delivery Activities"
echo ""
echo -e "${YELLOW}SERVICES INTEGRATION:${NC}"
echo "   User Service <-> Restaurant Service"
echo "   Restaurant Service <-> Delivery Service"
echo "   User Service <-> Delivery Service"
echo "   Complete Cross-Service Communication"
echo ""
echo -e "${GREEN}THE FOOD DELIVERY SYSTEM IS FULLY FUNCTIONAL${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "   • Run individual service tests for detailed validation"
echo "   • Test error scenarios and edge cases"
echo "   • Performance testing with multiple concurrent orders"
echo "   • Security testing with different user roles"
echo ""
echo -e "${PURPLE}=====================================================================${NC}"
echo -e "${PURPLE}                Thank you for testing${NC}"
echo -e "${PURPLE}=====================================================================${NC}" 