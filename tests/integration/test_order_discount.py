import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_order_with_percentage_discount(client):
    # Create product
    client.post("/products/", json={"name": "Product 1", "price": 100.0, "stock": 10})
    
    # Create discount
    client.post("/discounts/", json={
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 50.0,
        "is_active": True
    })
    
    # Create order
    response = client.post("/orders/", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SAVE20"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # Verify discount uses incremented
    disc_resp = client.get("/discounts/")
    discounts = disc_resp.json()
    save20 = next(d for d in discounts if d["code"] == "SAVE20")
    assert save20["current_uses"] == 1

def test_create_order_with_fixed_discount(client):
    client.post("/products/", json={"name": "Product 1", "price": 100.0, "stock": 10})
    client.post("/discounts/", json={
        "code": "FIXED10",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "is_active": True
    })
    
    response = client.post("/orders/", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 1}],
        "discount_code": "FIXED10"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 100.0
    assert data["discount_amount"] == 10.0
    assert data["total"] == 90.0

def test_create_order_invalid_discount(client):
    client.post("/products/", json={"name": "Product 1", "price": 100.0, "stock": 10})
    
    # Non-existent code
    response = client.post("/orders/", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 1}],
        "discount_code": "INVALID"
    })
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()

def test_create_order_insufficient_amount(client):
    client.post("/products/", json={"name": "Product 1", "price": 20.0, "stock": 10})
    client.post("/discounts/", json={
        "code": "MIN100",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 100.0,
        "is_active": True
    })
    
    response = client.post("/orders/", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 1}],
        "discount_code": "MIN100"
    })
    assert response.status_code == 400
    assert "minimum" in response.json()["detail"].lower()
