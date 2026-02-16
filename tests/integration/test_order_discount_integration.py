import pytest
from datetime import datetime, timedelta

def test_create_order_with_discount_success(client):
    # 1. Create a product
    prod_resp = client.post("/products", json={
        "name": "Test Product",
        "price": 100.0,
        "stock": 10
    })
    product_id = prod_resp.json()["id"]
    
    # 2. Create a discount
    client.post("/discounts", json={
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 50.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    # 3. Create order with discount
    order_payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "SAVE20"
    }
    # subtotal = 200.0, discount = 40.0, total = 160.0
    
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # 4. Verify discount uses increased
    disc_resp = client.get("/discounts")
    discount = next(d for d in disc_resp.json() if d["code"] == "SAVE20")
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount(client):
    prod_resp = client.post("/products", json={"name": "P1", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    order_payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "NONEXISTENT"
    }
    
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 400
    assert "Discount not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client):
    prod_resp = client.post("/products", json={"name": "P1", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    client.post("/discounts", json={
        "code": "EXPIRED",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 0.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "valid_until": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    order_payload = {
        "customer_name": "Jane",
        "customer_email": "jane@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "EXPIRED"
    }
    
    response = client.post("/orders", json=order_payload)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
