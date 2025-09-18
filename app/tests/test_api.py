import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.models import Customer, Order

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Savannah Microservice" in response.json()["message"]


def test_create_customer():
    """Test creating a customer"""
    customer_data = {
        "name": "Test Customer",
        "code": "TEST001",
        "phone_number": "+254712345678"
    }
    
    response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["code"] == customer_data["code"]
    assert data["phone_number"] == customer_data["phone_number"]
    assert "id" in data


def test_get_customers():
    """Test getting customers list"""
    response = client.get(
        "/api/v1/customers/",
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_customer_duplicate_code():
    """Test creating customer with duplicate code fails"""
    customer_data = {
        "name": "Another Customer",
        "code": "TEST001",  # Same code as previous test
        "phone_number": "+254712345679"
    }
    
    response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_order():
    """Test creating an order"""
    # First create a customer
    customer_data = {
        "name": "Order Customer",
        "code": "ORDER001",
        "phone_number": "+254712345680"
    }
    
    customer_response = client.post(
        "/api/v1/customers/",
        json=customer_data,
        headers={"Authorization": "Bearer mock-token"}
    )
    
    customer_id = customer_response.json()["id"]
    
    # Create order
    order_data = {
        "item": "Test Product",
        "amount": 99.99,
        "customer_id": customer_id
    }
    
    response = client.post(
        "/api/v1/orders/",
        json=order_data,
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["item"] == order_data["item"]
    assert data["amount"] == order_data["amount"]
    assert data["customer_id"] == customer_id
    assert "id" in data


def test_get_orders():
    """Test getting orders list"""
    response = client.get(
        "/api/v1/orders/",
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_order_invalid_customer():
    """Test creating order with invalid customer fails"""
    order_data = {
        "item": "Test Product",
        "amount": 99.99,
        "customer_id": 99999  # Non-existent customer
    }
    
    response = client.post(
        "/api/v1/orders/",
        json=order_data,
        headers={"Authorization": "Bearer mock-token"}
    )
    
    assert response.status_code == 400
    assert "Customer not found" in response.json()["detail"]


def test_unauthorized_access():
    """Test that endpoints require authentication"""
    response = client.get("/api/v1/customers/")
    assert response.status_code == 403  # Should require auth


def test_invalid_token():
    """Test invalid token handling"""
    response = client.get(
        "/api/v1/customers/",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401