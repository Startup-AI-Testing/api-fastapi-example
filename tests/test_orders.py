import pytest

def test_create_order_valid(client):
    # Setup: Create customer and products
    customer_res = client.post("/customers", json={"name": "Order Test", "email": "order@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod1_res = client.post("/products", json={"name": "P1", "description": "D1", "price": 100.0, "stock": 10})
    prod1_id = prod1_res.json()["id"]
    
    prod2_res = client.post("/products", json={"name": "P2", "description": "D2", "price": 50.0, "stock": 5})
    prod2_id = prod2_res.json()["id"]

    # Action: Create order
    order_data = {
        "customer_id": customer_id,
        "items": [
            {"product_id": prod1_id, "quantity": 2},
            {"product_id": prod2_id, "quantity": 1}
        ]
    }
    response = client.post("/orders", json=order_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["total"] == 250.0
    assert len(data["items"]) == 2
    
    # Verify stock reduction
    p1 = client.get(f"/products/{prod1_id}").json()
    p2 = client.get(f"/products/{prod2_id}").json()
    assert p1["stock"] == 8
    assert p2["stock"] == 4

def test_create_order_insufficient_stock(client):
    customer_res = client.post("/customers", json={"name": "Stock Test", "email": "stock@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod_res = client.post("/products", json={"name": "Low Stock", "description": "D", "price": 10.0, "stock": 5})
    prod_id = prod_res.json()["id"]

    order_data = {
        "customer_id": customer_id,
        "items": [{"product_id": prod_id, "quantity": 10}]
    }
    response = client.post("/orders", json=order_data)
    
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_cancel_order_restores_stock(client):
    customer_res = client.post("/customers", json={"name": "Cancel Test", "email": "cancel@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod_res = client.post("/products", json={"name": "Restorable", "description": "D", "price": 10.0, "stock": 10})
    prod_id = prod_res.json()["id"]

    order_res = client.post("/orders", json={
        "customer_id": customer_id,
        "items": [{"product_id": prod_id, "quantity": 5}]
    })
    order_id = order_res.json()["id"]
    
    # Verify stock reduced
    assert client.get(f"/products/{prod_id}").json()["stock"] == 5
    
    # Cancel order
    patch_res = client.patch(f"/orders/{order_id}/status", json={"status": "cancelled"})
    assert patch_res.status_code == 200
    
    # Verify stock restored
    assert client.get(f"/products/{prod_id}").json()["stock"] == 10

def test_delete_order_pending_only(client):
    customer_res = client.post("/customers", json={"name": "Delete Test", "email": "delete@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod_res = client.post("/products", json={"name": "Del", "description": "D", "price": 1.0, "stock": 10})
    prod_id = prod_res.json()["id"]

    # Pending order can be deleted
    order_pending = client.post("/orders", json={
        "customer_id": customer_id, "items": [{"product_id": prod_id, "quantity": 1}]
    }).json()
    res1 = client.delete(f"/orders/{order_pending['id']}")
    assert res1.status_code == 204

    # Confirmed order cannot be deleted
    order_confirmed = client.post("/orders", json={
        "customer_id": customer_id, "items": [{"product_id": prod_id, "quantity": 1}]
    }).json()
    patch_res = client.patch(f"/orders/{order_confirmed['id']}/status", json={"status": "confirmed"})
    assert patch_res.status_code == 200
    
    res2 = client.delete(f"/orders/{order_confirmed['id']}")
    assert res2.status_code == 400
    assert "only pending orders can be deleted" in res2.json()["detail"].lower()

def test_list_orders_filtering(client):
    customer_res = client.post("/customers", json={"name": "Filter Test", "email": "filter@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod_res = client.post("/products", json={"name": "Filter", "description": "D", "price": 1.0, "stock": 100})
    prod_id = prod_res.json()["id"]

    # Create two orders
    client.post("/orders", json={"customer_id": customer_id, "items": [{"product_id": prod_id, "quantity": 1}]})
    o2 = client.post("/orders", json={"customer_id": customer_id, "items": [{"product_id": prod_id, "quantity": 1}]}).json()
    patch_res = client.patch(f"/orders/{o2['id']}/status", json={"status": "shipped"})
    assert patch_res.status_code == 200

    # Filter by status
    res_pending = client.get("/orders", params={"status": "pending"})
    assert len(res_pending.json()) >= 1
    assert all(o["status"] == "pending" for o in res_pending.json())

    res_shipped = client.get("/orders", params={"status": "shipped"})
    assert len(res_shipped.json()) >= 1
    assert any(o["id"] == o2["id"] for o in res_shipped.json())

def test_customer_order_history(client):
    customer_res = client.post("/customers", json={"name": "History Test", "email": "history@example.com"})
    customer_id = customer_res.json()["id"]
    
    prod_res = client.post("/products", json={"name": "Hist", "description": "D", "price": 1.0, "stock": 10})
    prod_id = prod_res.json()["id"]

    client.post("/orders", json={"customer_id": customer_id, "items": [{"product_id": prod_id, "quantity": 1}]})
    
    response = client.get(f"/customers/{customer_id}/orders")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["customer_id"] == customer_id
