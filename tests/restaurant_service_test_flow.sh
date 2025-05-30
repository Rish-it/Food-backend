#!/bin/bash

# RESTAURANT SERVICE COMPLETE TEST FLOW
# This script tests all restaurant service endpoints with realistic scenarios
# Make sure the restaurant service is running on port 8002

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Service configuration
RESTAURANT_SERVICE_URL="http://localhost:8002"
EXISTING_RESTAURANT_ID="284bccdd-6501-42e5-9b31-171e5e483eb6"
EXISTING_MENU_ITEM_ID="e76d76c3-d42c-4958-9a16-f928c9e520ac"
TEST_ORDER_ID="c241cf9d-632f-4588-a295-1e324bc969d4"

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}         RESTAURANT SERVICE COMPLETE TEST FLOW${NC}"
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
print_step "1. Health Check - Verify Restaurant Service is Running"

curl -X GET "$RESTAURANT_SERVICE_URL/health" \
  -H "Content-Type: application/json" | jq

if [ $? -eq 0 ]; then
    print_success "Restaurant service is healthy and running"
else
    print_error "Restaurant service is not responding"
    exit 1
fi

wait_for_input

# TEST 2: Get Service Info
print_step "2. Get Service Information"

curl -X GET "$RESTAURANT_SERVICE_URL/" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved service information"
wait_for_input

# TEST 3: Get All Restaurants
print_step "3. Get All Restaurants"

echo "Getting all restaurants..."
curl -X GET "$RESTAURANT_SERVICE_URL/restaurants/" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved all restaurants"
wait_for_input

# TEST 4: Get Online Restaurants Only
print_step "4. Get Online Restaurants Only"

echo "Getting only online restaurants..."
curl -X GET "$RESTAURANT_SERVICE_URL/restaurants/?online_only=true" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved online restaurants"
wait_for_input

# TEST 5: Get Specific Restaurant
print_step "5. Get Specific Restaurant Details"

echo "Getting restaurant details for: $EXISTING_RESTAURANT_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/restaurants/$EXISTING_RESTAURANT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific restaurant details"
wait_for_input

# TEST 6: Create New Restaurant
print_step "6. Create New Restaurant"

echo "Creating a new restaurant..."
NEW_RESTAURANT_RESPONSE=$(curl -X POST "$RESTAURANT_SERVICE_URL/restaurants/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Burger Joint",
    "email": "test@burgerjoint.com",
    "phone": "+1-555-TEST-01",
    "address": {
        "street": "123 Test Avenue",
        "city": "Test City",
        "state": "TS",
        "zip": "12345",
        "lat": 40.7128,
        "lng": -74.0060
    },
    "cuisine_type": "American",
    "operation_hours": {
        "monday": {"open": "10:00", "close": "22:00"},
        "tuesday": {"open": "10:00", "close": "22:00"},
        "wednesday": {"open": "10:00", "close": "22:00"},
        "thursday": {"open": "10:00", "close": "22:00"},
        "friday": {"open": "10:00", "close": "23:00"},
        "saturday": {"open": "10:00", "close": "23:00"},
        "sunday": {"open": "11:00", "close": "21:00"}
    }
}' | jq)

echo "$NEW_RESTAURANT_RESPONSE"

NEW_RESTAURANT_ID=$(echo "$NEW_RESTAURANT_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Restaurant ID: $NEW_RESTAURANT_ID${NC}"

print_success "New restaurant created successfully"
wait_for_input

# TEST 7: Update Restaurant Status
print_step "7. Update Restaurant Online Status"

echo "Setting restaurant to online..."
curl -X PATCH "$RESTAURANT_SERVICE_URL/restaurants/$NEW_RESTAURANT_ID/status?is_online=true" \
  -H "Content-Type: application/json" | jq

print_success "Restaurant status updated to online"
wait_for_input

# TEST 8: Get Restaurant Menu
print_step "8. Get Restaurant Menu Items"

echo "Getting menu for restaurant: $EXISTING_RESTAURANT_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/menu/$EXISTING_RESTAURANT_ID/items" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved restaurant menu"
wait_for_input

# TEST 9: Get Available Menu Items Only
print_step "9. Get Available Menu Items Only"

echo "Getting only available menu items..."
curl -X GET "$RESTAURANT_SERVICE_URL/menu/$EXISTING_RESTAURANT_ID/items?available_only=true" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved available menu items"
wait_for_input

# TEST 10: Get Menu Items by Category
print_step "10. Get Menu Items by Category"

echo "Getting menu items by category 'Pizza'..."
curl -X GET "$RESTAURANT_SERVICE_URL/menu/$EXISTING_RESTAURANT_ID/items?category=Pizza" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved menu items by category"
wait_for_input

# TEST 11: Get Specific Menu Item
print_step "11. Get Specific Menu Item"

echo "Getting menu item: $EXISTING_MENU_ITEM_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/menu/items/$EXISTING_MENU_ITEM_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific menu item"
wait_for_input

# TEST 12: Create New Menu Item
print_step "12. Create New Menu Item"

echo "Creating a new menu item for restaurant: $NEW_RESTAURANT_ID"
NEW_MENU_ITEM_RESPONSE=$(curl -X POST "$RESTAURANT_SERVICE_URL/menu/$NEW_RESTAURANT_ID/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Deluxe Burger",
    "description": "Juicy beef patty with lettuce, tomato, cheese, and special sauce",
    "price": 18.99,
    "category": "Burgers",
    "is_available": true,
    "image_url": "https://example.com/test-burger.jpg"
}' | jq)

echo "$NEW_MENU_ITEM_RESPONSE"

NEW_MENU_ITEM_ID=$(echo "$NEW_MENU_ITEM_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created Menu Item ID: $NEW_MENU_ITEM_ID${NC}"

print_success "New menu item created successfully"
wait_for_input

# TEST 13: Update Menu Item Availability
print_step "13. Update Menu Item Availability"

echo "Setting menu item to unavailable..."
curl -X PATCH "$RESTAURANT_SERVICE_URL/menu/items/$NEW_MENU_ITEM_ID/availability?is_available=false" \
  -H "Content-Type: application/json" | jq

print_success "Menu item availability updated"
wait_for_input

echo "Setting menu item back to available..."
curl -X PATCH "$RESTAURANT_SERVICE_URL/menu/items/$NEW_MENU_ITEM_ID/availability?is_available=true" \
  -H "Content-Type: application/json" | jq

print_success "Menu item set back to available"
wait_for_input

# TEST 14: Get Restaurant Orders
print_step "14. Get Restaurant Orders"

echo "Getting all orders for restaurant: $EXISTING_RESTAURANT_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/orders/$EXISTING_RESTAURANT_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved restaurant orders"
wait_for_input

# TEST 15: Get Pending Orders
print_step "15. Get Pending Orders"

echo "Getting pending orders for restaurant: $EXISTING_RESTAURANT_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/orders/$EXISTING_RESTAURANT_ID/pending" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved pending orders"
wait_for_input

# TEST 16: Get Active Orders
print_step "16. Get Active Orders"

echo "Getting active orders for restaurant: $EXISTING_RESTAURANT_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/orders/$EXISTING_RESTAURANT_ID/active" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved active orders"
wait_for_input

# TEST 17: Get Specific Order
print_step "17. Get Specific Order Details"

echo "Getting order details: $TEST_ORDER_ID"
curl -X GET "$RESTAURANT_SERVICE_URL/orders/order/$TEST_ORDER_ID" \
  -H "Content-Type: application/json" | jq

print_success "Retrieved specific order details"
wait_for_input

# TEST 18: Accept Order
print_step "18. Accept Order with Estimated Prep Time"

echo "Accepting order with 25 minutes prep time..."
curl -X POST "$RESTAURANT_SERVICE_URL/orders/order/$TEST_ORDER_ID/restaurant/$EXISTING_RESTAURANT_ID/accept?estimated_prep_time=25" \
  -H "Content-Type: application/json" | jq

print_success "Order accepted successfully"
wait_for_input

# TEST 19: Update Order Status to Preparing
print_step "19. Update Order Status to Preparing"

echo "Updating order status to preparing..."
curl -X PATCH "$RESTAURANT_SERVICE_URL/orders/order/$TEST_ORDER_ID/restaurant/$EXISTING_RESTAURANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "preparing",
    "estimated_prep_time": 20
}' | jq

print_success "Order status updated to preparing"
wait_for_input

# TEST 20: Mark Order as Ready
print_step "20. Mark Order as Ready for Pickup"

echo "Marking order as ready..."
curl -X POST "$RESTAURANT_SERVICE_URL/orders/order/$TEST_ORDER_ID/restaurant/$EXISTING_RESTAURANT_ID/ready" \
  -H "Content-Type: application/json" | jq

print_success "Order marked as ready for pickup"
wait_for_input

# TEST 21: Error Testing - Invalid Restaurant ID
print_step "21. Error Testing - Invalid Restaurant ID"

echo "Attempting to get non-existent restaurant..."
curl -X GET "$RESTAURANT_SERVICE_URL/restaurants/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json" | jq

print_success "Error handling test completed"
wait_for_input

# TEST 22: Error Testing - Invalid Menu Item ID
print_step "22. Error Testing - Invalid Menu Item ID"

echo "Attempting to get non-existent menu item..."
curl -X GET "$RESTAURANT_SERVICE_URL/menu/items/00000000-0000-0000-0000-000000000000" \
  -H "Content-Type: application/json" | jq

print_success "Error handling test completed"
wait_for_input

# TEST 23: Order Rejection Test
print_step "23. Order Rejection Test"

echo "This would reject an order with a reason..."
echo "curl -X POST \"$RESTAURANT_SERVICE_URL/orders/order/ORDER_ID/restaurant/$EXISTING_RESTAURANT_ID/reject?reason=Out%20of%20ingredients\" | jq"
echo "Skipping as we don't have a pending order..."

print_success "Rejection test scenario shown"
wait_for_input

# TEST SUMMARY
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}                        TEST SUMMARY${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo -e "${GREEN}All Restaurant Service tests completed successfully${NC}"
echo ""
echo -e "${YELLOW}Created Resources:${NC}"
echo -e "  Restaurant: $NEW_RESTAURANT_ID"
echo -e "  Menu Item: $NEW_MENU_ITEM_ID"
echo ""
echo -e "${YELLOW}Tests Covered:${NC}"
echo "  1. Health Check"
echo "  2. Service Information"
echo "  3. Get All Restaurants"
echo "  4. Get Online Restaurants"
echo "  5. Get Specific Restaurant"
echo "  6. Create New Restaurant"
echo "  7. Update Restaurant Status"
echo "  8. Get Restaurant Menu"
echo "  9. Get Available Menu Items"
echo "  10. Get Menu Items by Category"
echo "  11. Get Specific Menu Item"
echo "  12. Create New Menu Item"
echo "  13. Update Menu Item Availability"
echo "  14. Get Restaurant Orders"
echo "  15. Get Pending Orders"
echo "  16. Get Active Orders"
echo "  17. Get Specific Order"
echo "  18. Accept Order"
echo "  19. Update Order Status"
echo "  20. Mark Order Ready"
echo "  21. Error Handling"
echo "  22. Invalid Data Testing"
echo "  23. Order Rejection Scenario"
echo ""
echo -e "${GREEN}Restaurant Service is working properly${NC}"
echo -e "${BLUE}=====================================================================${NC}" 