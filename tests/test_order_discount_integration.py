from datetime import datetime, timedelta

def test_create_order_with_discount_success(client):
    # 1. Create a product
    product_resp = client.post("/products/", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    # 2. Create a discount
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = datetime.utcnow() + timedelta(days=30)
    discount_data = {
        "code": "PROMO20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 50.0,
        "max_uses": 10,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    client.post("/discounts/", json=discount_data)
    
    # 3. Create an order with the discount
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "PROMO20"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "PROMO20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # 4. Verify discount uses incremented
    discount_resp = client.get("/discounts/")
    discount = next(d for d in discount_resp.json() if d["code"] == "PROMO20")
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount(client):
    # 1. Create a product
    product_resp = client.post("/products/", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    # 2. Create an order with an invalid discount
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "INVALID_CODE"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_order_with_expired_discount(client):
    # 1. Create a product
    product_resp = client.post("/products/", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    # 2. Create an expired discount
    valid_from = datetime.utcnow() - timedelta(days=10)
    valid_until = datetime.utcnow() - timedelta(days=1)
    discount_data = {
        "code": "EXPIRED",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 0.0,
        "max_uses": 10,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    client.post("/discounts/", json=discount_data)
    
    # 3. Create an order with the expired discount
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "EXPIRED"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
