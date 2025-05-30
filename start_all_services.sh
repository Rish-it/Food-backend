#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Log file
LOG_FILE="deploy/services.log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check if a service is running
check_service() {
    local port=$1
    local service=$2
    if curl -s "http://localhost:$port/health" > /dev/null; then
        log "${GREEN}[PASS] $service is running on port $port${NC}"
        return 0
    else
        log "${RED}[FAIL] $service is not running on port $port${NC}"
        return 1
    fi
}

# Function to start a service
start_service() {
    local service=$1
    local port=$2
    local dir=$3
    
    log "Starting $service..."
    cd "$dir" || exit 1
    uvicorn main:app --host 0.0.0.0 --port "$port" --reload >> "$LOG_FILE" 2>&1 &
    local pid=$!
    cd ..
    echo "$pid"
}

# Create log directory and file
mkdir -p deploy
> "$LOG_FILE"
log "Starting Food Delivery Microservices..."

# Start services
USER_PID=$(start_service "User Service" 8001 "user_service")
RESTAURANT_PID=$(start_service "Restaurant Service" 8002 "restaurant_service")
DELIVERY_PID=$(start_service "Delivery Service" 8003 "delivery_service")

# Wait for services to start
log "Waiting for services to start..."
sleep 5

# Check if all services are running
USER_OK=false
RESTAURANT_OK=false
DELIVERY_OK=false

for i in {1..5}; do
    if check_service 8001 "User Service"; then
        USER_OK=true
    fi
    if check_service 8002 "Restaurant Service"; then
        RESTAURANT_OK=true
    fi
    if check_service 8003 "Delivery Service"; then
        DELIVERY_OK=true
    fi
    
    if $USER_OK && $RESTAURANT_OK && $DELIVERY_OK; then
        break
    fi
    
    log "Retrying in 2 seconds..."
    sleep 2
done

# Final status check
if $USER_OK && $RESTAURANT_OK && $DELIVERY_OK; then
    log "${GREEN}[SUCCESS] All services started successfully!${NC}"
    log "User Service: http://localhost:8001/docs"
    log "Restaurant Service: http://localhost:8002/docs"
    log "Delivery Service: http://localhost:8003/docs"
else
    log "${RED}[FAIL] Some services failed to start${NC}"
    if ! $USER_OK; then
        log "User Service failed to start"
    fi
    if ! $RESTAURANT_OK; then
        log "Restaurant Service failed to start"
    fi
    if ! $DELIVERY_OK; then
        log "Delivery Service failed to start"
    fi
fi

# Handle script termination
cleanup() {
    log "Stopping all services..."
    kill $USER_PID $RESTAURANT_PID $DELIVERY_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
wait 