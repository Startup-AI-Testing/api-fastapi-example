from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from datetime import datetime, timedelta

def test_create_order_with_valid_discount(client: TestClient, db: Session):
    # Create a product
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Create a discount
    discount = models.Discount(
        code="SAVE20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 2}],
            "discount_code": "SAVE20"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # Verify discount usage increased
    db.refresh(discount)
    assert discount.current_uses == 1

def test_create_order_with_invalid_discount(client: TestClient, db: Session):
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "NONEXISTENT"
        }
    )
    
    assert response.status_code == 400
    assert "Discount not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client: TestClient, db: Session):
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    discount = models.Discount(
        code="EXPIRED",
        discount_type="fixed_amount",
        discount_value=10.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "EXPIRED"
        }
    )
    
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()

def test_create_order_with_insufficient_amount(client: TestClient, db: Session):
    product = models.Product(name="Test Product", price=20.0, stock=10)
    db.add(product)
    
    discount = models.Discount(
        code="MIN50",
        discount_type="fixed_amount",
        discount_value=10.0,
        min_order_amount=50.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "MIN50"
        }
    )
    
    assert response.status_code == 400
    assert "minimum required" in response.json()["detail"].lower()
