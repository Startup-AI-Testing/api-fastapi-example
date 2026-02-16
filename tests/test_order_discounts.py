from datetime import datetime, timedelta

def test_create_order_with_valid_discount(client):
    # 1. Create a product
    prod_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    # 2. Create a discount
    client.post("/discounts", json={
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 50.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    # 3. Create order with discount
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "SAVE20"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    
    # Subtotal: 2 * 100 = 200
    # Discount: 20% of 200 = 40
    # Total: 200 - 40 = 160
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # 4. Verify discount uses incremented
    disc_resp = client.get("/discounts")
    discount = next(d for d in disc_resp.json() if d["code"] == "SAVE20")
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount(client):
    prod_resp = client.post("/products", json={"name": "Test Product 2", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "NONEXISTENT"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Discount not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client):
    prod_resp = client.post("/products", json={"name": "Test Product 3", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    client.post("/discounts", json={
        "code": "EXPIRED",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "valid_from": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "valid_until": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "EXPIRED"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()

def test_create_order_below_min_amount(client):
    prod_resp = client.post("/products", json={"name": "Cheap Product", "price": 10.0, "stock": 10})
    product_id = prod_resp.json()["id"]
    
    client.post("/discounts", json={
        "code": "MIN100",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 100.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "MIN100"
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "below the minimum" in response.json()["detail"].lower()
