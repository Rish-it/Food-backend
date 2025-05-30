.PHONY: build up down logs clean test health help

# Default target
help:
	@echo "Food Delivery Backend - Docker Commands"
	@echo "======================================"
	@echo "build     - Build the Docker images"
	@echo "up        - Start all services"
	@echo "down      - Stop all services"
	@echo "logs      - View logs from all services"
	@echo "clean     - Remove all containers and volumes"
	@echo "test      - Run the API tests"
	@echo "health    - Check service health"
	@echo "restart   - Restart all services"
	@echo "shell     - Get a shell in the backend container"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Wait a few seconds for all services to be ready"
	@echo "GraphQL Gateway: http://localhost:8000"
	@echo "User Service: http://localhost:8001/docs"
	@echo "Restaurant Service: http://localhost:8002/docs"
	@echo "Delivery Service: http://localhost:8003/docs"

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up everything
clean:
	docker-compose down -v
	docker system prune -f

# Check service health
health:
	python docker-test.py

# Run tests
test:
	docker-compose exec backend python test_live_endpoints.py

# Restart services
restart: down up

# Get shell access
shell:
	docker-compose exec backend bash

# Quick start (build and run)
start: build up 