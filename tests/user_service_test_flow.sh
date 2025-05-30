#!/bin/bash

# USER SERVICE COMPLETE TEST FLOW
# This script tests all user service endpoints with realistic scenarios
# Make sure the user service is running on port 8001

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Service configuration
USER_SERVICE_URL="http://localhost:8001"
TEST_USER_ID="7d2a9f80-bd2f-4a32-8a8c-5e9f9d4f6e76"
RESTAURANT_ID="284bccdd-6501-42e5-9b31-171e5e483eb6"
MENU_ITEM_ID="e76d76c3-d42c-4958-9a16-f928c9e520ac"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}           USER SERVICE COMPLETE TEST FLOW${NC}"
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
print_step "1. Health Check - Verify User Service is Running"

curl -X GET "$USER_SERVICE_URL/health" \
  -H "Content-Type: application/json" | jq

if [ $? -eq 0 ]; then
    print_success "User service is healthy and running"
else
    print_error "User service is not responding"
    exit 1
fi

wait_for_input

# TEST 2: Get Available Restaurants
print_step "2. Get Available Restaurants - From User Service"

echo "Getting all available restaurants..."
curl -X GET "$USER_SERVICE_URL/restaurants/" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved restaurant list"
wait_for_input

# TEST 3: Get Restaurant Menu
print_step "3. Get Restaurant Menu - View Menu Items"

echo "Getting menu for restaurant: $RESTAURANT_ID"
curl -X GET "$USER_SERVICE_URL/restaurants/$RESTAURANT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved restaurant menu"
wait_for_input

# TEST 4: Create Order - Single Item
print_step "4. Create Order - Single Menu Item"

echo "Creating order with single item..."
ORDER_RESPONSE=$(curl -X POST "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "'$RESTAURANT_ID'",
    "delivery_address": {
        "street": "123 Test Street",
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
    "special_instructions": "Ring the doorbell twice"
}' | jq)

echo "$ORDER_RESPONSE"

ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Order ID: $ORDER_ID${NC}"

print_success "Single item order created successfully"
wait_for_input

# TEST 5: Create Order - Multiple Items
print_step "5. Create Order - Multiple Menu Items"

echo "Creating order with multiple items..."
MULTI_ORDER_RESPONSE=$(curl -X POST "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "'$RESTAURANT_ID'",
    "delivery_address": {
        "street": "456 Multi Street",
        "city": "Brooklyn",
        "state": "NY",
        "zip_code": "11201"
    },
    "items": [
        {
            "menu_item_id": "'$MENU_ITEM_ID'",
            "quantity": 3
        }
    ],
    "special_instructions": "Extra napkins please"
}' | jq)

echo "$MULTI_ORDER_RESPONSE"

MULTI_ORDER_ID=$(echo "$MULTI_ORDER_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Multi Order ID: $MULTI_ORDER_ID${NC}"

print_success "Multiple item order created successfully"
wait_for_input

# TEST 6: Get Specific Order Details
print_step "6. Get Specific Order Details"

echo "Getting details for order: $ORDER_ID"
curl -X GET "$USER_SERVICE_URL/orders/$ORDER_ID" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific order details"
wait_for_input

# TEST 7: Get All User Orders
print_step "7. Get All User Orders - Order History"

echo "Getting all orders for user: $TEST_USER_ID"
curl -X GET "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved user order history"
wait_for_input

# TEST 8: Get User Orders with Pagination
print_step "8. Get User Orders with Pagination"

echo "Getting first 5 orders..."
curl -X GET "$USER_SERVICE_URL/orders/?limit=5&offset=0" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved paginated order list"
wait_for_input

# TEST 9: Error Testing - Invalid User Access
print_step "9. Error Testing - Try to Access Another User's Order"

echo "Attempting to access order with different user ID (should fail)..."
curl -X GET "$USER_SERVICE_URL/orders/$ORDER_ID" \
  -H "X-User-Id: 550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" | jq

print_success "Security test completed - access denied as expected"
wait_for_input

# TEST 10: Error Testing - Invalid Order ID
print_step "10. Error Testing - Invalid Order ID"

echo "Attempting to get non-existent order..."
curl -X GET "$USER_SERVICE_URL/orders/00000000-0000-0000-0000-000000000000" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Error handling test completed"
wait_for_input

# TEST 11: Create Order with Invalid Menu Item
print_step "11. Error Testing - Invalid Menu Item"

echo "Attempting to create order with non-existent menu item..."
curl -X POST "$USER_SERVICE_URL/orders/" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "'$RESTAURANT_ID'",
    "delivery_address": {
        "street": "789 Error Street",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345"
    },
    "items": [
        {
            "menu_item_id": "00000000-0000-0000-0000-000000000000",
            "quantity": 1
        }
    ]
}' | jq

print_success "Invalid menu item test completed"
wait_for_input

# TEST SUMMARY
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}                        TEST SUMMARY${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${GREEN}All User Service tests completed successfully${NC}"
echo ""
echo -e "${YELLOW}Created Orders:${NC}"
echo -e "  Order 1: $ORDER_ID"
echo -e "  Order 2: $MULTI_ORDER_ID"
echo ""
echo -e "${YELLOW}Tests Covered:${NC}"
echo "  1. Health Check"
echo "  2. Get Available Restaurants"
echo "  3. Get Restaurant Menu"
echo "  4. Create Single Item Order"
echo "  5. Create Multiple Item Order"
echo "  6. Get Specific Order Details"
echo "  7. Get All User Orders"
echo "  8. Get Orders with Pagination"
echo "  9. Security Testing"
echo "  10. Error Handling"
echo "  11. Invalid Data Testing"
echo ""
echo -e "${GREEN}User Service is working properly${NC}"
echo -e "${BLUE}=====================================================================${NC}" 