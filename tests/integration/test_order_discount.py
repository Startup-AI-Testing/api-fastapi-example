from app.models import Product, Discount

def test_create_order_with_valid_discount(client, db):
    # Setup product
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    # Setup discount
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}],
        "discount_code": "SUMMER2024"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 100.0
    assert data["discount_amount"] == 20.0
    assert data["total"] == 80.0
    assert data["discount_code"] == "SUMMER2024"
    
    # Check current_uses incremented
    db.refresh(discount)
    assert discount.current_uses == 1

def test_create_order_with_invalid_discount_code(client, db):
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}],
        "discount_code": "INVALID"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Discount code not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client, db):
    from datetime import datetime, timedelta
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    
    discount = Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}],
        "discount_code": "EXPIRED"
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Discount has expired" in response.json()["detail"]

def test_create_order_without_discount(client, db):
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 1}]
    }
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 100.0
    assert data["discount_amount"] == 0.0
    assert data["total"] == 100.0
    assert data["discount_code"] is None
