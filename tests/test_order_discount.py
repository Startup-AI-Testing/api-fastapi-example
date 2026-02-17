from datetime import datetime, timedelta
from app import models

def test_create_order_with_valid_discount(client, db):
    # Create product
    p1 = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(p1)
    db.commit()
    
    # Create discount
    d1 = models.Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(d1)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": p1.id, "quantity": 1}],
        "discount_code": "SUMMER2024"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 1000.0
    assert data["discount_code"] == "SUMMER2024"
    assert data["discount_amount"] == 200.0
    assert data["total"] == 800.0
    
    # Verify usage increment
    db.refresh(d1)
    assert d1.current_uses == 1

def test_create_order_with_invalid_discount(client, db):
    # Create product
    p1 = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(p1)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": p1.id, "quantity": 1}],
        "discount_code": "INVALID"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 404

def test_create_order_without_discount(client, db):
    # Create product
    p1 = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(p1)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": p1.id, "quantity": 1}]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 1000.0
    assert data["discount_code"] is None
    assert data["discount_amount"] == 0.0
    assert data["total"] == 1000.0
