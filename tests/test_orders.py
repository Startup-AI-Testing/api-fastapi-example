import pytest

def test_create_order(client):
    # Setup: Create customer and product
    client.post("/customers/", json={"name": "Buyer", "email": "buyer@example.com"})
    client.post("/products/", json={"name": "Laptop", "price": 1000.0, "stock": 5, "category": "Tech"})
    
    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total"] == 2000.0
    assert len(data["items"]) == 1
    assert data["items"][0]["subtotal"] == 2000.0
    
    # Check stock reduction
    prod_res = client.get("/products/1")
    assert prod_res.json()["stock"] == 3

def test_create_order_insufficient_stock(client):
    client.post("/customers/", json={"name": "Buyer", "email": "buyer2@example.com"})
    client.post("/products/", json={"name": "Phone", "price": 500.0, "stock": 1, "category": "Tech"})
    
    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        }
    )
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_cancel_order_restores_stock(client):
    client.post("/customers/", json={"name": "Buyer", "email": "buyer3@example.com"})
    client.post("/products/", json={"name": "Tablet", "price": 300.0, "stock": 10, "category": "Tech"})
    
    # Create order
    order_res = client.post(
        "/orders/",
        json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 5}]}
    )
    order_id = order_res.json()["id"]
    
    # Verify stock reduced
    assert client.get("/products/1").json()["stock"] == 5
    
    # Cancel order
    client.patch(f"/orders/{order_id}/status", json={"status": "cancelled"})
    
    # Verify stock restored
    assert client.get("/products/1").json()["stock"] == 10

def test_delete_pending_order(client):
    client.post("/customers/", json={"name": "Buyer", "email": "buyer4@example.com"})
    client.post("/products/", json={"name": "Mouse", "price": 20.0, "stock": 10, "category": "Tech"})
    
    order_res = client.post(
        "/orders/",
        json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]}
    )
    order_id = order_res.json()["id"]
    
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204
    
    # Verify stock restored
    assert client.get("/products/1").json()["stock"] == 10

def test_list_orders_filters(client):
    client.post("/customers/", json={"name": "C1", "email": "c1@test.com"})
    client.post("/products/", json={"name": "P1", "price": 10.0, "stock": 10, "category": "A"})
    
    # Order 1
    client.post("/orders/", json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]})
    # Order 2
    client.post("/orders/", json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]})
    
    response = client.get("/orders/?customer_id=1")
    assert len(response.json()) >= 2
