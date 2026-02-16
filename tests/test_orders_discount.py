from datetime import datetime, timedelta

def test_create_order_with_discount(client):
    # 1. Create a product
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "description": "Description",
        "price": 100.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    # 2. Create a discount
    client.post("/discounts", json={
        "code": "ORDER_DISCOUNT",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 50.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })

    # 3. Create order with discount
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "ORDER_DISCOUNT"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "ORDER_DISCOUNT"
    assert data["discount_amount"] == 20.0
    assert data["total"] == 180.0

def test_create_order_invalid_discount(client):
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "description": "Description",
        "price": 100.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    # Try with non-existent discount
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "INVALID"
    })
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()

def test_create_order_insufficient_amount_for_discount(client):
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "description": "Description",
        "price": 20.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    client.post("/discounts", json={
        "code": "MIN_50",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 50.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })

    # Order amount is 20.0, min is 50.0
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "MIN_50"
    })
    assert response.status_code == 400
    assert "minimum" in response.json()["detail"].lower()
