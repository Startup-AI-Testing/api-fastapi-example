from datetime import datetime, timedelta

def test_create_order_with_discount(client):
    # 1. Create a product
    prod_resp = client.post("/products/", json={"name": "Test Product", "price": 100.0, "stock": 100})
    product_id = prod_resp.json()["id"]

    # 2. Create a discount
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    client.post(
        "/discounts/",
        json={
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat()
        }
    )

    # 3. Create order with discount
    order_resp = client.post(
        "/orders/",
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

def test_create_order_with_invalid_discount(client):
    prod_resp = client.post("/products/", json={"name": "Test Product", "price": 100.0, "stock": 100})
    product_id = prod_resp.json()["id"]

    order_resp = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
            "discount_code": "INVALID"
        }
    )
    assert order_resp.status_code == 400
    assert "Discount code not found" in order_resp.json()["detail"]
