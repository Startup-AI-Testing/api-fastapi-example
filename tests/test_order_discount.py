import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import Product, Discount

@pytest.fixture
def setup_data(db: Session):
    # Create a product
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Create a discount
    discount = Discount(
        code="SAVE20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    db.refresh(product)
    db.refresh(discount)
    return product, discount

def test_create_order_with_discount(client, db: Session, setup_data):
    product, discount = setup_data
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 2}],
        "discount_code": "SAVE20"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # Verify discount uses increased
    db.refresh(discount)
    assert discount.current_uses == 1

def test_create_order_with_invalid_discount(client, db: Session, setup_data):
    product, _ = setup_data
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}],
        "discount_code": "INVALID"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()

def test_create_order_with_expired_discount(client, db: Session, setup_data):
    product, _ = setup_data
    
    # Create expired discount
    expired_discount = Discount(
        code="EXPIRED",
        discount_type="fixed_amount",
        discount_value=10.0,
        min_order_amount=0.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=2),
        valid_until=datetime.now() - timedelta(days=1),
        is_active=True
    )
    db.add(expired_discount)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}],
        "discount_code": "EXPIRED"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()

def test_create_order_with_insufficient_amount(client, db: Session, setup_data):
    product, discount = setup_data
    
    cheap_product = Product(name="Cheap Product", price=10.0, stock=10)
    db.add(cheap_product)
    db.commit()
    db.refresh(cheap_product)
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": cheap_product.id, "quantity": 1}],
        "discount_code": "SAVE20"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "below the minimum" in response.json()["detail"].lower()
