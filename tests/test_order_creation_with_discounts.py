from datetime import datetime, timedelta

def test_create_order_with_discount(client):
    # 1. Create a product
    product_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    # 2. Create a discount
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = valid_from + timedelta(days=30)
    client.post(
        "/discounts",
        json={
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    
    # 3. Create order with discount
    order_resp = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product_id, "quantity": 2}],
            "discount_code": "SAVE20"
        }
    )
    
    assert order_resp.status_code == 201
    data = order_resp.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # 4. Verify discount uses increased
    discount_resp = client.get("/discounts")
    discount = next(d for d in discount_resp.json() if d["code"] == "SAVE20")
    assert discount["current_uses"] == 1

def test_create_order_invalid_discount(client):
    product_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    # Order with non-existent discount
    order_resp = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
            "discount_code": "NONEXISTENT"
        }
    )
    assert order_resp.status_code == 404
    assert "Discount not found" in order_resp.json()["detail"]

def test_create_order_min_amount_not_reached(client):
    product_resp = client.post("/products", json={"name": "Cheap Product", "price": 10.0, "stock": 10})
    product_id = product_resp.json()["id"]
    
    client.post(
        "/discounts",
        json={
            "code": "MIN100",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    )
    
    order_resp = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
            "discount_code": "MIN100"
        }
    )
    assert order_resp.status_code == 400
    assert "Minimum order amount" in order_resp.json()["detail"]
