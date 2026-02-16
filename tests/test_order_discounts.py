import pytest
from datetime import datetime, timedelta
from app import models

def test_create_order_with_percentage_discount(client, db):
    # Create product
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Create discount
    discount = models.Discount(
        code="SAVE20",
        discount_type="percentage",
        discount_value=20.0,
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1)
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "discount_code": "SAVE20",
            "items": [{"product_id": product.id, "quantity": 2}]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    assert data["discount_code"] == "SAVE20"
    
    # Verify discount uses incremented
    db.refresh(discount)
    assert discount.current_uses == 1

def test_create_order_with_fixed_amount_discount(client, db):
    # Create product
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Create discount
    discount = models.Discount(
        code="FIXED10",
        discount_type="fixed_amount",
        discount_value=10.0,
        is_active=True
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "discount_code": "FIXED10",
            "items": [{"product_id": product.id, "quantity": 1}]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 100.0
    assert data["discount_amount"] == 10.0
    assert data["total"] == 90.0

def test_create_order_with_invalid_discount(client, db):
    # Create product
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "discount_code": "INVALID",
            "items": [{"product_id": product.id, "quantity": 1}]
        }
    )
    
    assert response.status_code == 400
    assert "Discount code not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client, db):
    # Create product
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Create expired discount
    discount = models.Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "discount_code": "EXPIRED",
            "items": [{"product_id": product.id, "quantity": 1}]
        }
    )
    
    assert response.status_code == 400
    assert "Discount is expired" in response.json()["detail"]

def test_create_order_with_insufficient_amount(client, db):
    # Create product
    product = models.Product(name="Test Product", price=50.0, stock=10)
    db.add(product)
    
    # Create discount with min amount 100
    discount = models.Discount(
        code="MIN100",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        is_active=True
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "discount_code": "MIN100",
            "items": [{"product_id": product.id, "quantity": 1}]
        }
    )
    
    assert response.status_code == 400
    assert "Minimum order amount not met" in response.json()["detail"]
