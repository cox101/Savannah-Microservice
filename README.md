# Savannah Microservice

A Python microservice for managing customers and their orders with SMS notifications, built with FastAPI, PostgreSQL, and Africa's Talking SMS service.

## Features

- **Customer Management**: Create, read, update, and delete customers
- **Order Management**: Handle customer orders with automatic SMS notifications
- **Authentication**: Secure API endpoints using OpenID Connect (Auth0)
- **SMS Notifications**: Automatic SMS alerts via Africa's Talking when orders are created
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Testing**: Comprehensive unit tests with pytest
- **CI/CD**: GitHub Actions pipeline for automated testing and deployment
- **Containerization**: Docker support for easy deployment

## Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: OpenID Connect (Auth0)
- **SMS Service**: Africa's Talking
- **Testing**: pytest with coverage
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with service information

### Authentication
All API endpoints require Bearer token authentication via OpenID Connect.

### Customers
- `POST /api/v1/customers/` - Create a new customer
- `GET /api/v1/customers/` - List all customers
- `GET /api/v1/customers/{id}` - Get customer by ID
- `GET /api/v1/customers/code/{code}` - Get customer by code
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer

### Orders
- `POST /api/v1/orders/` - Create a new order (triggers SMS notification)
- `GET /api/v1/orders/` - List all orders (with optional customer filter)
- `GET /api/v1/orders/{id}` - Get order by ID
- `PUT /api/v1/orders/{id}` - Update order
- `DELETE /api/v1/orders/{id}` - Delete order

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Docker (optional)

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/cox101/Savannah-Microservice.git
cd Savannah-Microservice
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual configuration values
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

This will start both the application and PostgreSQL database.

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/savannah_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Auth0 / OpenID Connect
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_AUDIENCE=your-api-identifier
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# Africa's Talking
AFRICAS_TALKING_USERNAME=sandbox
AFRICAS_TALKING_API_KEY=your-api-key
AFRICAS_TALKING_SANDBOX=true

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### Auth0 Setup

1. Create an Auth0 account and application
2. Configure the application as an API
3. Set the appropriate callback URLs
4. Update the environment variables with your Auth0 configuration

### Africa's Talking Setup

1. Sign up for Africa's Talking account
2. Get your API credentials
3. For production, set `AFRICAS_TALKING_SANDBOX=false`

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_api.py -v
```

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Linting
flake8 app/

# Type checking
mypy app/ --ignore-missing-imports

# Code formatting
black app/
```

### Database Migrations

Create new migrations:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

## API Usage Examples

### Authentication

For development, you can use the mock authentication by sending `mock-token` as the Bearer token:

```bash
curl -H "Authorization: Bearer mock-token" http://localhost:8000/api/v1/customers/
```

### Create a Customer

```bash
curl -X POST "http://localhost:8000/api/v1/customers/" \
  -H "Authorization: Bearer mock-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "code": "CUST001",
    "phone_number": "+254712345678"
  }'
```

### Create an Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer mock-token" \
  -H "Content-Type: application/json" \
  -d '{
    "item": "Product Name",
    "amount": 99.99,
    "customer_id": 1
  }'
```

## Deployment

### CI/CD Pipeline

The project includes a GitHub Actions pipeline that:

1. Runs tests and linting
2. Builds Docker images
3. Deploys to production (configuration needed)

### Production Deployment

1. Set up a PostgreSQL database
2. Configure environment variables for production
3. Deploy using Docker or your preferred platform
4. Run database migrations
5. Configure Auth0 for production domain
6. Set up Africa's Talking production credentials

## Project Structure

```
├── app/
│   ├── api/                 # API route handlers
│   ├── core/                # Core configuration and dependencies
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas for validation
│   ├── services/            # Business logic and external services
│   └── tests/               # Test files
├── alembic/                 # Database migration files
├── .github/workflows/       # CI/CD pipeline
├── docker-compose.yml       # Docker compose configuration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── main.py                 # Application entry point
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.