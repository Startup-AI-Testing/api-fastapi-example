import pytest

def test_create_order(client):
    # Setup
    client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    client.post("/products/", json={"name": "Laptop", "price": 1000.0, "stock": 5})
    
    # Action
    response = client.post("/orders/", json={
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    })
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == 1
    assert data["total"] == 2000.0
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == 1
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["unit_price"] == 1000.0
    assert data["items"][0]["subtotal"] == 2000.0
    
    # Check stock reduction
    prod_resp = client.get("/products/1")
    assert prod_resp.json()["stock"] == 3


def test_create_order_insufficient_stock(client):
    client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    client.post("/products/", json={"name": "Laptop", "price": 1000.0, "stock": 1})
    
    response = client.post("/orders/", json={
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    })
    
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_cancel_order_restores_stock(client):
    client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    client.post("/products/", json={"name": "Laptop", "price": 1000.0, "stock": 5})
    client.post("/orders/", json={
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    })
    
    # Cancel order
    response = client.patch("/orders/1/status", json={"status": "cancelled"})
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    
    # Check stock restored
    prod_resp = client.get("/products/1")
    assert prod_resp.json()["stock"] == 5


def test_delete_non_pending_order_fails(client):
    client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    client.post("/products/", json={"name": "Laptop", "price": 1000.0, "stock": 5})
    client.post("/orders/", json={
        "customer_id": 1,
        "items": [{"product_id": 1, "quantity": 2}]
    })
    
    # Confirm order
    client.patch("/orders/1/status", json={"status": "confirmed"})
    
    # Try to delete
    response = client.delete("/orders/1")
    assert response.status_code == 400
    assert "Only pending orders can be deleted" in response.json()["detail"]


def test_list_orders_filters(client):
    client.post("/customers/", json={"name": "User 1", "email": "u1@ex.com"})
    client.post("/customers/", json={"name": "User 2", "email": "u2@ex.com"})
    client.post("/products/", json={"name": "P1", "price": 10, "stock": 100})
    
    client.post("/orders/", json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]})
    client.post("/orders/", json={"customer_id": 2, "items": [{"product_id": 1, "quantity": 1}]})
    
    # Filter by customer_id
    response = client.get("/orders/?customer_id=1")
    assert len(response.json()) == 1
    assert response.json()[0]["customer_id"] == 1
