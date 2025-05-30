# Food Delivery Microservices

A scalable microservices-based food delivery system with three core services: User, Restaurant, and Delivery.

## Project Structure

```
.
├── user_service/           # User management service
│   ├── Dockerfile         # Service container configuration
│   ├── main.py           # FastAPI application entry point
│   └── ...
├── restaurant_service/    # Restaurant management service
│   ├── Dockerfile
│   ├── main.py
│   └── ...
├── delivery_service/      # Delivery management service
│   ├── Dockerfile
│   ├── main.py
│   └── ...
├── deploy/               # Deployment configuration
│   ├── config/          # Configuration files
│   │   ├── alembic.ini  # Database migration config
│   │   └── pytest.ini   # Test configuration
│   ├── nginx/           # Nginx configuration
│   │   └── nginx.conf   # API Gateway config
│   └── docker-compose.yml # Service orchestration
├── migrations/          # Database migrations
├── tests/              # Test suite
│   ├── integration/    # Integration tests
│   └── unit/          # Unit tests
├── postman/           # API documentation
└── scripts/           # Utility scripts
```

## Features

- [PASS] Microservices Architecture
- [PASS] API Gateway with Nginx
- [PASS] PostgreSQL Database
- [PASS] Redis Caching
- [PASS] Docker Containerization
- [PASS] Comprehensive Testing
- [PASS] API Documentation
- [PASS] Database Migrations

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL 14
- Redis

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd food-delivery
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
./start_all_services.sh
```

4. Run the tests:
```bash
python run_tests.py
```

## API Documentation

- User Service: http://localhost:8001/docs
- Restaurant Service: http://localhost:8002/docs
- Delivery Service: http://localhost:8003/docs

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/integration/test_end_to_end_flow.py

# Run with coverage
pytest --cov=.
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Docker Commands

```bash
# Build and start all services
docker-compose -f deploy/docker-compose.yml up --build

# Stop all services
docker-compose -f deploy/docker-compose.yml down

# View logs
docker-compose -f deploy/docker-compose.yml logs -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
