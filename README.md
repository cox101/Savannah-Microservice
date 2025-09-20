# Savannah Microservice

A comprehensive Python microservice built with Django REST Framework, featuring customer and order management with OAuth2 authentication and SMS notifications via Africa's Talking API.

## 🚀 Features

- **RESTful API** for customers and orders management
- **OAuth2 Authentication** using OpenID Connect
- **SMS Notifications** via Africa's Talking API
- **Asynchronous Task Processing** with Celery
- **Comprehensive Testing** with 80%+ coverage
- **CI/CD Pipeline** with GitHub Actions
- **Containerized Deployment** with Docker
- **Kubernetes Support** with Helm charts
- **Infrastructure as Code** with Ansible playbooks
- **Security Best Practices** implemented throughout

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [SMS Integration](#-sms-integration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Security](#-security)
- [Contributing](#-contributing)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Load Balancer │    │      CDN        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │              Kubernetes Cluster               │
         │  ┌─────────────────┐  ┌─────────────────┐    │
         │  │   Django App    │  │  Celery Workers │    │
         │  │    (Pods)       │  │     (Pods)      │    │
         │  └─────────────────┘  └─────────────────┘    │
         │           │                     │             │
         │  ┌─────────▼─────────┐ ┌────────▼──────────┐  │
         │  │   PostgreSQL      │ │      Redis        │  │
         │  │   (Database)      │ │   (Cache/Queue)   │  │
         │  └───────────────────┘ └───────────────────┘  │
         └───────────────────────────────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │            External Services                  │
         │  ┌─────────────────┐  ┌─────────────────┐    │
         │  │ Africa's Talking│  │    Monitoring   │    │
         │  │   SMS Gateway   │  │   & Logging     │    │
         │  └─────────────────┘  └─────────────────┘    │
         └───────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Savannah-Microservice.git
   cd Savannah-Microservice
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Start Celery worker** (in another terminal)
   ```bash
   celery -A savannah_microservice worker --loglevel=info
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at `http://localhost:8000`

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000/api`
- Production: `https://api.savannah-microservice.com/api`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register new user |
| POST | `/auth/login/` | User login |
| POST | `/auth/logout/` | User logout |
| GET | `/auth/profile/` | Get user profile |
| PATCH | `/auth/profile/` | Update user profile |
| POST | `/auth/change-password/` | Change password |
| GET | `/auth/token-info/` | Get token information |

### Customer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/` | List customers |
| POST | `/customers/` | Create customer |
| GET | `/customers/{id}/` | Get customer details |
| PATCH | `/customers/{id}/` | Update customer |
| DELETE | `/customers/{id}/` | Delete customer |
| GET | `/customers/{id}/orders/` | Get customer orders |
| GET | `/customers/{id}/stats/` | Get customer statistics |
| GET | `/customers/search/?q=query` | Search customers |

### Order Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | List orders |
| POST | `/orders/` | Create order (triggers SMS) |
| GET | `/orders/{id}/` | Get order details |
| PATCH | `/orders/{id}/` | Update order |
| DELETE | `/orders/{id}/` | Delete order |
| PATCH | `/orders/{id}/update_status/` | Update order status |
| POST | `/orders/{id}/cancel/` | Cancel order |
| POST | `/orders/{id}/resend_sms/` | Resend SMS notification |
| GET | `/orders/analytics/` | Get order analytics |
| GET | `/orders/search/?q=query` | Search orders |

### Example API Usage

#### 1. Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
  }'
```

#### 2. Create OAuth2 application
```bash
curl -X POST http://localhost:8000/api/auth/create-app/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Mobile App"}'
```

#### 3. Login and get access token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret"
  }'
```

#### 4. Create a customer
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone_number": "+254700123456"
  }'
```

#### 5. Create an order (triggers SMS notification)
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "customer-uuid",
    "item": "Laptop Computer",
    "amount": "999.99",
    "quantity": 1,
    "notes": "Urgent delivery required"
  }'
```

## 🔐 Authentication

The service uses OAuth2 with OpenID Connect for authentication:

1. **Create OAuth2 Application**: Use the `/auth/create-app/` endpoint
2. **User Registration**: Register users via `/auth/register/`
3. **Login**: Exchange credentials for access token via `/auth/login/`
4. **API Access**: Include token in `Authorization: Bearer <token>` header
5. **Token Management**: Use `/auth/token-info/` to verify token status

### Security Features

- **Password Validation**: Minimum 8 characters with complexity requirements
- **Token Expiration**: 1-hour access token lifetime
- **CORS Protection**: Configurable allowed origins
- **XSS Protection**: Content Security Policy headers
- **SQL Injection Protection**: Django ORM with parameterized queries
- **Rate Limiting**: Implemented at API Gateway level

## 📱 SMS Integration

The service integrates with Africa's Talking SMS API for notifications:

### Configuration

```env
AFRICAS_TALKING_USERNAME=your-username
AFRICAS_TALKING_API_KEY=your-api-key
AFRICAS_TALKING_SENDER_ID=SAVANNAH
```

### SMS Triggers

1. **Order Creation**: Automatic SMS sent when order is created
2. **Status Updates**: SMS sent for important status changes (shipped, delivered, cancelled)
3. **Manual Resend**: Use `/orders/{id}/resend_sms/` endpoint

### Phone Number Format

- International format required: `+254700123456`
- Local Kenyan numbers automatically converted: `0700123456` → `+254700123456`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run with pytest
pytest

# Run specific test file
pytest customers/tests/test_models.py

# Run with verbose output
pytest -v
```

### Test Coverage

The project maintains 80%+ test coverage across:

- **Unit Tests**: Model validation, serializer logic, utility functions
- **Integration Tests**: API endpoints, authentication flow
- **Mock Tests**: External service integrations (SMS, email)

### Test Configuration

- **Database**: Separate test database automatically created
- **Fixtures**: Reusable test data in `tests/conftest.py`
- **Mocking**: External APIs mocked for reliable testing
- **Parallel Execution**: Tests run in parallel for faster feedback

## 🚀 Deployment

### Production Environment Variables

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=api.savannah-microservice.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://redis-host:6379/0
```

### Docker Deployment

```bash
# Build production image
docker build -t savannah-microservice:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Install with Helm
helm install savannah-microservice ./helm/savannah-microservice \
  --set image.tag=latest \
  --set secrets.secretKey=your-secret-key \
  --set secrets.databaseUrl=postgresql://... \
  --set ingress.hosts[0].host=api.savannah-microservice.com
```

### Ansible Deployment

```bash
# Deploy to servers
ansible-playbook -i inventory ansible/playbook.yml \
  --vault-password-file vault_pass.txt
```

## 📊 Monitoring

### Health Checks

- **Application Health**: `/api/auth/health/`
- **Database Health**: Automatic Django health checks
- **Redis Health**: Connection verification in health endpoint

### Logging

- **Application Logs**: Structured JSON logging
- **Access Logs**: Nginx access logs
- **Error Tracking**: Integration with Sentry (optional)

### Metrics

- **Request Metrics**: Response time, error rates
- **Business Metrics**: Orders created, SMS sent
- **Infrastructure Metrics**: CPU, memory, disk usage

## 🔒 Security

### Security Measures Implemented

1. **Authentication & Authorization**
   - OAuth2 with OpenID Connect
   - Role-based access control
   - Token-based authentication

2. **Data Protection**
   - Input validation and sanitization
   - SQL injection prevention
   - XSS protection headers

3. **Network Security**
   - HTTPS enforcement
   - CORS configuration
   - Security headers (HSTS, CSP)

4. **Infrastructure Security**
   - Container security scanning
   - Dependency vulnerability scanning
   - Regular security updates

### Security Best Practices

- Keep dependencies updated
- Use environment variables for secrets
- Regular security audits
- Monitor for suspicious activity
- Implement rate limiting
- Use secure communication protocols

## 📈 Performance

### Optimization Features

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Redis caching for frequently accessed data
- **Async Processing**: Celery for background tasks
- **Connection Pooling**: Database connection optimization
- **Static File Serving**: Optimized static file delivery

### Scaling Considerations

- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: Read replicas, connection pooling
- **Cache Scaling**: Redis clustering
- **Load Balancing**: Application-level load balancing

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and write tests
4. Run tests: `pytest`
5. Run linting: `flake8 .`
6. Format code: `black .`
7. Commit changes: `git commit -m "Description"`
8. Push to branch: `git push origin feature-name`
9. Create Pull Request

### Code Standards

- **PEP 8**: Python code style guide
- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **Type Hints**: Use type annotations where appropriate
- **Docstrings**: Document all functions and classes

### Testing Requirements

- All new features must include tests
- Maintain minimum 80% test coverage
- Integration tests for API endpoints
- Mock external service calls

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:

- **Email**: support@savannah-microservice.com
- **Documentation**: [Wiki](https://github.com/yourusername/Savannah-Microservice/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Savannah-Microservice/issues)

## 🙏 Acknowledgments

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Africa's Talking API](https://africastalking.com/)
- [OAuth2 Toolkit](https://django-oauth-toolkit.readthedocs.io/)
- [Celery](https://docs.celeryproject.org/)

---

**Built with ❤️ for Savannah Informatics Technical Interview**