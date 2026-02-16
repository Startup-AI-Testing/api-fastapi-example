from datetime import datetime, timedelta

def test_create_order_with_valid_discount(client):
    # 1. Create a product
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "price": 100.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    # 2. Create a discount
    discount_code = "SAVE20"
    client.post("/discounts", json={
        "code": discount_code,
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 50.0,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True,
        "max_uses": 10
    })

    # 3. Create order with discount
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": discount_code
    }
    response = client.post("/orders", json=order_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == discount_code
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0

    # 4. Verify discount uses increased
    discount_resp = client.get("/discounts")
    discounts = discount_resp.json()
    discount = next(d for d in discounts if d["code"] == discount_code)
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount_code(client):
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "price": 100.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "INVALID"
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 400
    assert "Discount not found" in response.json()["detail"]

def test_create_order_with_insufficient_amount_for_discount(client):
    product_resp = client.post("/products", json={
        "name": "Test Product",
        "price": 20.0,
        "stock": 10
    })
    product_id = product_resp.json()["id"]

    discount_code = "MIN100"
    client.post("/discounts", json={
        "code": discount_code,
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 100.0,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })

    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": discount_code
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 400
    assert "Order amount does not meet minimum requirement" in response.json()["detail"]
