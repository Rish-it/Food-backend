# 🍕 Food Delivery System - Complete Test Flows

This directory contains comprehensive test scripts for all three microservices in the food delivery system. Each script provides detailed testing with pretty-printed JSON output and realistic scenarios.

## 📋 Prerequisites

### Required Software
- **jq** - For JSON pretty printing
  ```bash
  # macOS
  brew install jq
  
  # Ubuntu/Debian
  sudo apt-get install jq
  
  # CentOS/RHEL
  sudo yum install jq
  ```

### Running Services
Make sure all services are running before executing tests:

```bash
# Terminal 1 - User Service
cd user_service && uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Restaurant Service  
cd restaurant_service && uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3 - Delivery Service
cd delivery_service && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## 🧪 Test Scripts Overview

### 1. Individual Service Tests

#### 🧑‍💼 User Service Test Flow
**File:** `user_service_test_flow.sh`

Tests all user service functionality including:
- ✅ Health checks
- ✅ Restaurant browsing
- ✅ Order creation (single & multiple items)
- ✅ Order history and details
- ✅ Pagination
- ✅ Security testing
- ✅ Error handling

```bash
# Make executable and run
chmod +x tests/user_service_test_flow.sh
./tests/user_service_test_flow.sh
```

#### 🏪 Restaurant Service Test Flow
**File:** `restaurant_service_test_flow.sh`

Tests all restaurant service functionality including:
- ✅ Restaurant management (CRUD)
- ✅ Menu management (CRUD)
- ✅ Order processing (accept/reject/prepare)
- ✅ Status updates
- ✅ Order filtering
- ✅ Error handling

```bash
# Make executable and run
chmod +x tests/restaurant_service_test_flow.sh
./tests/restaurant_service_test_flow.sh
```

#### 🚚 Delivery Service Test Flow
**File:** `delivery_service_test_flow.sh`

Tests all delivery service functionality including:
- ✅ Delivery agent management (CRUD)
- ✅ Location tracking
- ✅ Order assignment
- ✅ Delivery status updates
- ✅ Complete delivery lifecycle
- ✅ Error handling

```bash
# Make executable and run
chmod +x tests/delivery_service_test_flow.sh
./tests/delivery_service_test_flow.sh
```

### 2. Complete System Integration Test

#### 🌟 End-to-End System Test Flow
**File:** `complete_system_test_flow.sh`

Tests the complete food delivery workflow across all services:

**🔄 Complete Journey Tested:**
1. **System Health Check** - Verify all services are running
2. **Customer Browsing** - Browse restaurants and menus
3. **Order Creation** - Customer places order
4. **Restaurant Processing** - Restaurant receives and accepts order
5. **Order Preparation** - Kitchen prepares food
6. **Delivery Assignment** - Find and assign delivery agent
7. **Pickup Process** - Driver picks up from restaurant
8. **Delivery Progress** - Real-time tracking
9. **Delivery Completion** - Order delivered to customer
10. **Post-Delivery** - Order history and analytics

```bash
# Make executable and run
chmod +x tests/complete_system_test_flow.sh
./tests/complete_system_test_flow.sh
```

## 🚀 Quick Start Guide

### Step 1: Start All Services
```bash
# Use the provided startup script (if available)
./start_all_services.sh

# Or start each service individually (see Prerequisites above)
```

### Step 2: Run Individual Service Tests
```bash
# Test each service individually first
./tests/user_service_test_flow.sh
./tests/restaurant_service_test_flow.sh  
./tests/delivery_service_test_flow.sh
```

### Step 3: Run Complete System Test
```bash
# Test the complete end-to-end workflow
./tests/complete_system_test_flow.sh
```

## 📊 Test Data Used

All test scripts use consistent test data:

- **Test User ID:** `7d2a9f80-bd2f-4a32-8a8c-5e9f9d4f6e76`
- **Restaurant ID:** `284bccdd-6501-42e5-9b31-171e5e483eb6`
- **Menu Item ID:** `e76d76c3-d42c-4958-9a16-f928c9e520ac`

## 🎨 Features

### Pretty Output
- **Color-coded output** for easy readability
- **JSON pretty printing** with jq
- **Progress indicators** and status messages
- **Interactive prompts** to control test flow pace

### Comprehensive Coverage
- **Happy path scenarios** - Normal operation flows
- **Error scenarios** - Invalid data and edge cases
- **Security testing** - Authentication and authorization
- **Integration testing** - Cross-service communication

### Realistic Scenarios
- **Multi-step workflows** mimicking real user behavior
- **Realistic test data** with proper addresses and details
- **Status transitions** following business logic
- **Performance insights** with timing information

## 🔧 Customization

### Modifying Test Data
Edit the variables at the top of each script:

```bash
# Service URLs
USER_SERVICE_URL="http://localhost:8001"
RESTAURANT_SERVICE_URL="http://localhost:8002"
DELIVERY_SERVICE_URL="http://localhost:8003"

# Test IDs
TEST_USER_ID="your-user-id"
RESTAURANT_ID="your-restaurant-id"
MENU_ITEM_ID="your-menu-item-id"
```

### Adding New Tests
Each script follows a consistent structure:

```bash
print_step "Test Description"
print_info "What this test does..."

# Your curl command here
curl -X GET "http://localhost:8001/endpoint" | jq

print_success "Test completed successfully"
wait_for_input
```

## 🐛 Troubleshooting

### Common Issues

1. **jq not found**
   ```bash
   # Install jq first (see Prerequisites)
   brew install jq  # macOS
   ```

2. **Service not responding**
   ```bash
   # Check if services are running
   curl http://localhost:8001/health
   curl http://localhost:8002/health  
   curl http://localhost:8003/health
   ```

3. **Permission denied**
   ```bash
   # Make scripts executable
   chmod +x tests/*.sh
   ```

4. **Test data not found**
   ```bash
   # Run the test data creation script first
   python create_test_data.py
   ```

### Debug Mode
Add `-x` flag to any script for detailed execution:

```bash
bash -x tests/user_service_test_flow.sh
```

## 📈 Test Coverage Matrix

| Service | CRUD | Authentication | Error Handling | Integration |
|---------|------|---------------|----------------|-------------|
| User Service | ✅ | ✅ | ✅ | ✅ |
| Restaurant Service | ✅ | ❌ | ✅ | ✅ |
| Delivery Service | ✅ | ❌ | ✅ | ✅ |

## 🎯 Expected Results

### Successful Test Run
- All health checks pass ✅
- JSON responses are properly formatted 🎨
- Status codes are appropriate (200, 201, 404, etc.) ✅
- Business logic flows correctly ✅
- Cross-service communication works ✅

### Test Output Example
```json
{
  "service": "user-service",
  "status": "healthy", 
  "version": "1.0.0"
}
✅ SUCCESS: User service is healthy and running
```

## 💡 Tips for Best Results

1. **Run tests in order** - Individual services first, then complete system
2. **Check service logs** if any test fails
3. **Use consistent test data** across all scripts
4. **Monitor resource usage** during testing
5. **Clean up test data** between runs if needed

## 🔄 Continuous Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Run Service Tests
  run: |
    chmod +x tests/*.sh
    ./tests/user_service_test_flow.sh
    ./tests/restaurant_service_test_flow.sh
    ./tests/delivery_service_test_flow.sh
    ./tests/complete_system_test_flow.sh
```

## 📞 Support

If you encounter any issues with the test scripts:

1. Check the **Troubleshooting** section above
2. Verify all **Prerequisites** are met
3. Review service logs for detailed error information
4. Ensure test data exists in the database

---

**Happy Testing! 🚀🍕📱** 