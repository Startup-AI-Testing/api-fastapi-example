
def test_create_order_with_discount(client):
    # 1. Create a product
    product_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]

    # 2. Create a discount
    client.post(
        "/discounts",
        json={
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0
        }
    )

    # 3. Create order with discount
    order_resp = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
            "discount_code": "SAVE20"
        }
    )
    assert order_resp.status_code == 201
    data = order_resp.json()
    assert data["subtotal"] == 100.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 20.0
    assert data["total"] == 80.0

    # 4. Verify discount uses incremented
    discount_resp = client.get("/discounts")
    discount_data = next(d for d in discount_resp.json() if d["code"] == "SAVE20")
    assert discount_data["current_uses"] == 1
    # Wait, I need to make sure the implementation increments it.
    # I'll check this after implementation.

def test_create_order_invalid_discount(client):
    product_resp = client.post("/products", json={"name": "Test Product", "price": 100.0, "stock": 10})
    product_id = product_resp.json()["id"]

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
    assert "not found" in order_resp.json()["detail"].lower()

def test_create_order_discount_min_amount(client):
    product_resp = client.post("/products", json={"name": "Cheap Product", "price": 10.0, "stock": 10})
    product_id = product_resp.json()["id"]

    client.post(
        "/discounts",
        json={
            "code": "MIN100",
            "discount_type": "fixed_amount",
            "discount_value": 5.0,
            "min_order_amount": 100.0
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
    assert "below the minimum amount" in order_resp.json()["detail"]
