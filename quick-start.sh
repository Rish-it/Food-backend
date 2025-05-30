#!/bin/bash

set -e

echo "Food Delivery Backend - Quick Start"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test service health
echo "🏥 Checking service health..."
python docker-test.py

echo ""
echo "🎉 Food Delivery Backend is ready!"
echo ""
echo "Service URLs:"
echo "- GraphQL Gateway: http://localhost:8000/graphql"
echo "- User Service API: http://localhost:8001/docs"
echo "- Restaurant Service API: http://localhost:8002/docs"
echo "- Delivery Service API: http://localhost:8003/docs"
echo ""
echo "Commands:"
echo "- View logs: docker-compose logs -f"
echo "- Stop services: docker-compose down"
echo "- Run tests: docker-compose exec backend python test_live_endpoints.py" 