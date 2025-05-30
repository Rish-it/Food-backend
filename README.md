# Food Delivery Backend Microservices

A comprehensive food delivery backend system built with FastAPI microservices, featuring user management, restaurant operations, delivery tracking, and a unified GraphQL API gateway.

## Architecture + Detailed Workflow

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │Restaurant Service│   │Delivery Service │
│    (Port 8001)  │    │    (Port 8002)   │   │   (Port 8003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ GraphQL Gateway │
                    │   (Port 8000)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  PostgreSQL DB  │
                    │   (Port 5432)   │
                    └─────────────────┘
```

### Service Responsibilities

**User Service (Port 8001)**
- User registration and authentication
- Order placement and tracking
- Restaurant discovery and menu browsing
- Rating and review management

**Restaurant Service (Port 8002)**
- Restaurant profile management
- Menu item CRUD operations
- Order processing and status updates
- Restaurant availability management

**Delivery Service (Port 8003)**
- Delivery agent management
- Order assignment to agents
- Real-time delivery tracking
- Agent location and availability updates

**GraphQL Gateway (Port 8000)**
- Unified API endpoint for all services
- Cross-service data aggregation
- Single point of entry for frontend applications

### Detailed Workflow

#### Order Placement Flow
1. **User browses restaurants** → User Service fetches restaurant list from Restaurant Service
2. **User views menu** → User Service retrieves menu items from Restaurant Service
3. **User places order** → User Service creates order and notifies Restaurant Service
4. **Restaurant accepts order** → Restaurant Service updates order status and finds available delivery agent
5. **Order assigned to agent** → Restaurant Service notifies Delivery Service with agent assignment
6. **Agent picks up order** → Delivery Service updates order status to "picked_up"
7. **Agent delivers order** → Delivery Service marks order as "delivered"
8. **User rates experience** → User Service stores rating for restaurant and delivery

#### Data Flow
- **Inter-service communication**: HTTP REST APIs
- **Database**: Shared PostgreSQL database with service-specific schemas
- **Authentication**: JWT tokens for user sessions
- **Real-time updates**: WebSocket connections for order status updates

#### API Patterns
- **REST APIs**: CRUD operations for each service
- **GraphQL**: Unified query interface across all services
- **Health checks**: `/health` endpoints for monitoring
- **Documentation**: OpenAPI/Swagger docs at `/docs` endpoints

## Regular Setup (Development)

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Git

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb food_delivery

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/food_delivery"
export USER_SERVICE_PORT=8001
export RESTAURANT_SERVICE_PORT=8002
export DELIVERY_SERVICE_PORT=8003
export GRAPHQL_GATEWAY_PORT=8000

# Run migrations
alembic upgrade head

# Create test data
python create_test_data.py
```

### 3. Start Services
```bash
# Terminal 1 - User Service
cd user_service
python main.py

# Terminal 2 - Restaurant Service  
cd restaurant_service
python main.py

# Terminal 3 - Delivery Service
cd delivery_service
python main.py

# Terminal 4 - GraphQL Gateway
cd graphql_gateway
python main.py
```

### 4. Test APIs
```bash
# Run comprehensive tests
python test_live_endpoints.py

# Or use pytest
pytest tests/
```

### API Documentation (Regular Setup)
- User Service: http://localhost:8001/docs
- Restaurant Service: http://localhost:8002/docs
- Delivery Service: http://localhost:8003/docs
- GraphQL Gateway: http://localhost:8000/graphql

## Docker Setup (Recommended)

### Prerequisites
- Docker and Docker Compose
- Make (optional, for convenience commands)

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd backend

# Option 1: Using Make (recommended)
make start

# Option 2: Using shell script
./quick-start.sh

# Option 3: Manual Docker Compose
docker-compose up --build -d
```

### Available Make Commands
```bash
make help          # Show all available commands
make build         # Build Docker images
make up            # Start all services
make down          # Stop all services
make logs          # View service logs
make test          # Run API tests
make health        # Check service health
make clean         # Clean up containers and volumes
make restart       # Restart all services
make shell         # Get shell access to backend container
```

### Manual Docker Commands
```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service health
python docker-test.py

# Run comprehensive tests
docker-compose exec backend python test_live_endpoints.py

# Stop services
docker-compose down

# Clean up everything
docker-compose down -v && docker system prune -f
```

### Service Access (Docker)
Once started, access the services at:
- **GraphQL Gateway**: http://localhost:8000/graphql
- **User Service API**: http://localhost:8001/docs
- **Restaurant Service API**: http://localhost:8002/docs  
- **Delivery Service API**: http://localhost:8003/docs

### Docker Features
- **Automatic database setup**: PostgreSQL container with migrations
- **Test data creation**: Sample data automatically loaded
- **Health checks**: Built-in service monitoring
- **Log aggregation**: Centralized logging via Docker Compose
- **Volume persistence**: Database data persisted across restarts

### Troubleshooting

#### Common Issues
1. **Port conflicts**: Ensure ports 8000-8003 and 5432 are available
2. **Database connection**: Check if PostgreSQL container is running healthy
3. **Service startup**: Allow 30-60 seconds for all services to fully initialize

#### Debug Commands
```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs [service-name]

# Get shell access to backend container
make shell

# Restart specific service
docker-compose restart [service-name]
```

## Testing

### Automated Testing
```bash
# Docker environment
make test

# Regular environment
python test_live_endpoints.py
pytest tests/
```

### Manual Testing
Use the provided Postman collection in `postman/Food_Delivery_API_Collection.json` or access the interactive API documentation.

## Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Database**: PostgreSQL 15 with asyncpg driver
- **ORM**: SQLAlchemy 2.0 (async)
- **APIs**: REST + GraphQL (Strawberry)
- **Authentication**: JWT with passlib
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest, httpx
- **Documentation**: OpenAPI/Swagger, GraphQL introspection

## Production Considerations

- Update environment variables for production
- Use proper secret management (e.g., HashiCorp Vault)
- Configure proper logging and monitoring
- Set up external database with connection pooling
- Implement rate limiting and proper authentication
- Configure CORS settings appropriately
- Set up load balancing for high availability
- Use container orchestration (Kubernetes) for scaling
