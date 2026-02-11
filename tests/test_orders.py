import pytest
from app.models import OrderStatus

def test_create_order(client):
    # 1. Create a customer
    customer_resp = client.post("/customers/", json={"name": "Test User", "email": "test@example.com"})
    customer_id = customer_resp.json()["id"]

    # 2. Create products
    prod1 = client.post("/products/", json={"name": "Product 1", "description": "Desc 1", "price": 100.0, "stock": 10})
    prod2 = client.post("/products/", json={"name": "Product 2", "description": "Desc 2", "price": 50.0, "stock": 5})
    p1_id = prod1.json()["id"]
    p2_id = prod2.json()["id"]

    # 3. Create order
    order_data = {
        "customer_id": customer_id,
        "items": [
            {"product_id": p1_id, "quantity": 2},
            {"product_id": p2_id, "quantity": 1}
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["status"] == "pending"
    assert data["total"] == 250.0 # (100*2) + (50*1)
    assert len(data["items"]) == 2

    # 4. Check stock reduced
    p1_after = client.get(f"/products/{p1_id}").json()
    p2_after = client.get(f"/products/{p2_id}").json()
    assert p1_after["stock"] == 8
    assert p2_after["stock"] == 4

def test_create_order_insufficient_stock(client):
    customer_resp = client.post("/customers/", json={"name": "Test User", "email": "test@example.com"})
    customer_id = customer_resp.json()["id"]

    prod = client.post("/products/", json={"name": "Limited Prod", "description": "Desc", "price": 10.0, "stock": 2})
    p_id = prod.json()["id"]

    order_data = {
        "customer_id": customer_id,
        "items": [{"product_id": p_id, "quantity": 5}]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    # Check stock NOT reduced
    p_after = client.get(f"/products/{p_id}").json()
    assert p_after["stock"] == 2

def test_cancel_order_restores_stock(client):
    customer_resp = client.post("/customers/", json={"name": "Test User", "email": "test@example.com"})
    customer_id = customer_resp.json()["id"]

    prod = client.post("/products/", json={"name": "Restorable", "description": "Desc", "price": 10.0, "stock": 10})
    p_id = prod.json()["id"]

    # Create order
    order_data = {
        "customer_id": customer_id,
        "items": [{"product_id": p_id, "quantity": 3}]
    }
    order_resp = client.post("/orders/", json=order_data)
    order_id = order_resp.json()["id"]
    
    # Check stock reduced
    assert client.get(f"/products/{p_id}").json()["stock"] == 7

    # Cancel order
    cancel_resp = client.patch(f"/orders/{order_id}/status", json={"status": "cancelled"})
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # Check stock restored
    assert client.get(f"/products/{p_id}").json()["stock"] == 10

def test_delete_order_pending(client):
    customer_resp = client.post("/customers/", json={"name": "Test User", "email": "test@example.com"})
    customer_id = customer_resp.json()["id"]
    prod = client.post("/products/", json={"name": "P", "description": "D", "price": 1.0, "stock": 1})
    p_id = prod.json()["id"]

    order_resp = client.post("/orders/", json={"customer_id": customer_id, "items": [{"product_id": p_id, "quantity": 1}]})
    order_id = order_resp.json()["id"]

    # Delete pending order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204
    
    # Verify gone
    assert client.get(f"/orders/{order_id}").status_code == 404

def test_delete_order_non_pending_fails(client):
    customer_resp = client.post("/customers/", json={"name": "Test User", "email": "test@example.com"})
    customer_id = customer_resp.json()["id"]
    prod = client.post("/products/", json={"name": "P", "description": "D", "price": 1.0, "stock": 1})
    p_id = prod.json()["id"]

    order_resp = client.post("/orders/", json={"customer_id": customer_id, "items": [{"product_id": p_id, "quantity": 1}]})
    order_id = order_resp.json()["id"]

    # Confirm order
    client.patch(f"/orders/{order_id}/status", json={"status": "confirmed"})

    # Try to delete
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 400
    assert "Only pending orders can be deleted" in response.json()["detail"]

def test_list_orders_filters(client):
    # Setup: 2 customers, multiple orders
    c1 = client.post("/customers/", json={"name": "C1", "email": "c1@ex.com"}).json()["id"]
    c2 = client.post("/customers/", json={"name": "C2", "email": "c2@ex.com"}).json()["id"]
    p = client.post("/products/", json={"name": "P", "description": "D", "price": 1.0, "stock": 100}).json()["id"]

    o1 = client.post("/orders/", json={"customer_id": c1, "items": [{"product_id": p, "quantity": 1}]}).json()["id"]
    o2 = client.post("/orders/", json={"customer_id": c2, "items": [{"product_id": p, "quantity": 1}]}).json()["id"]
    
    # Confirm o2
    client.patch(f"/orders/{o2}/status", json={"status": "confirmed"})

    # Filter by customer_id
    resp = client.get(f"/orders/?customer_id={c1}")
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == o1

    # Filter by status
    resp = client.get("/orders/?status=confirmed")
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == o2
