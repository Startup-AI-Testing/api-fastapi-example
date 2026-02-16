import pytest
from datetime import datetime, timedelta

def test_create_order_with_percentage_discount(client):
    # 1. Create a product
    prod_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]

    # 2. Create a discount
    client.post(
        "/discounts",
        json={
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 150.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )

    # 3. Create order with discount (amount 200 > 150)
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 2}],
        "discount_code": "SAVE20"
    }
    response = client.post("/orders", json=order_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    assert data["discount_code"] == "SAVE20"

    # 4. Verify discount uses increased
    disc_resp = client.get("/discounts")
    discount = next(d for d in disc_resp.json() if d["code"] == "SAVE20")
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount(client):
    prod_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = prod_resp.json()["id"]

    # Discount with min amount 500
    client.post(
        "/discounts",
        json={
            "code": "BIGSPENDER",
            "discount_type": "fixed_amount",
            "discount_value": 50.0,
            "min_order_amount": 500.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )

    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product_id, "quantity": 1}],
        "discount_code": "BIGSPENDER"
    }
    response = client.post("/orders", json=order_data)
    
    assert response.status_code == 400
    assert "below the minimum required" in response.json()["detail"]
