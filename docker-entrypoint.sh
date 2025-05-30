#!/bin/bash

set -e

echo "Starting Food Delivery Backend Services..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head

echo "Creating test data..."
python create_test_data.py

# Start all services in background
echo "Starting User Service on port 8001..."
cd /app/user_service
python main.py &
USER_PID=$!

echo "Starting Restaurant Service on port 8002..."
cd /app/restaurant_service  
python main.py &
RESTAURANT_PID=$!

echo "Starting Delivery Service on port 8003..."
cd /app/delivery_service
python main.py &
DELIVERY_PID=$!

echo "Starting GraphQL Gateway on port 8000..."
cd /app/graphql_gateway
python main.py &
GRAPHQL_PID=$!

# Wait a bit for services to start
sleep 5

echo "All services started successfully!"
echo "User Service: http://localhost:8001"
echo "Restaurant Service: http://localhost:8002" 
echo "Delivery Service: http://localhost:8003"
echo "GraphQL Gateway: http://localhost:8000"
echo "API Documentation:"
echo "  - User Service: http://localhost:8001/docs"
echo "  - Restaurant Service: http://localhost:8002/docs"
echo "  - Delivery Service: http://localhost:8003/docs"
echo "  - GraphQL Gateway: http://localhost:8000/graphql"

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $USER_PID $RESTAURANT_PID $DELIVERY_PID $GRAPHQL_PID 2>/dev/null || true
    wait
    echo "All services stopped."
    exit 0
}

# Trap SIGTERM and SIGINT
trap cleanup SIGTERM SIGINT

# Wait for all background processes
wait 