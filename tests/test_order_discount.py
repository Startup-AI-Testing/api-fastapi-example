
def test_create_order_with_percentage_discount(client):
    # Create product
    client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    # Create discount
    client.post("/discounts", json={
        "code": "SAVE20", "discount_type": "percentage", "discount_value": 20.0, "min_order_amount": 50.0
    })
    
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SAVE20"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    assert data["discount_code"] == "SAVE20"
    
    # Check discount uses
    discount_resp = client.get("/discounts")
    assert discount_resp.json()[0]["current_uses"] == 1

def test_create_order_with_fixed_discount(client):
    # Create product
    client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    # Create discount
    client.post("/discounts", json={
        "code": "FIXED50", "discount_type": "fixed_amount", "discount_value": 50.0
    })
    
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "FIXED50"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 50.0
    assert data["total"] == 150.0

def test_create_order_with_invalid_discount_code(client):
    # Create product
    client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "INVALID"
    })
    
    assert response.status_code == 404
    assert "Discount not found" in response.json()["detail"]

def test_create_order_with_expired_discount(client):
    from datetime import datetime, timedelta
    # Create product
    client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    # Create expired discount
    client.post("/discounts", json={
        "code": "EXPIRED",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_until": (datetime.utcnow() - timedelta(days=1)).isoformat()
    })
    
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "EXPIRED"
    })
    
    assert response.status_code == 400
    assert "Discount has expired" in response.json()["detail"]
