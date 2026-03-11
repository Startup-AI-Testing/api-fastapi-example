import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_reserve_stock_endpoint(client):
    # 1. Create a product
    response = client.post("/products/", json={"name": "Test Product", "price": 10.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    
    # 2. Restock the product (admin)
    response = client.post("/inventory/restock", json={
        "product_id": product_id,
        "quantity": 10,
        "reference": "INITIAL"
    })
    assert response.status_code == 200
    
    # 3. Reserve stock
    response = client.post("/inventory/reserve", json={
        "product_id": product_id,
        "quantity": 2
    })
    assert response.status_code == 200
    reservation = response.json()
    assert reservation["quantity"] == 2
    assert reservation["status"] == "active"
    
    # 4. Check availability
    response = client.get(f"/inventory/product/{product_id}")
    assert response.status_code == 200
    inventory = response.json()
    assert inventory["quantity_available"] == 8
    assert inventory["quantity_reserved"] == 2

def test_confirm_reservation_endpoint(client):
    # 1. Create and restock product
    response = client.post("/products/", json={"name": "Test Product 2", "price": 20.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    client.post("/inventory/restock", json={"product_id": product_id, "quantity": 10, "reference": "REF"})
    
    # 2. Reserve stock
    response = client.post("/inventory/reserve", json={"product_id": product_id, "quantity": 3})
    reservation_id = response.json()["id"]
    
    # 3. Confirm reservation
    response = client.post(f"/inventory/reserve/{reservation_id}/confirm", json={"order_id": 101})
    assert response.status_code == 200
    
    # 4. Check inventory
    response = client.get(f"/inventory/product/{product_id}")
    inventory = response.json()
    assert inventory["quantity_available"] == 7
    assert inventory["quantity_reserved"] == 0
    assert inventory["quantity_sold"] == 3

def test_release_reservation_endpoint(client):
    # 1. Create and restock product
    response = client.post("/products/", json={"name": "Test Product 3", "price": 30.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    client.post("/inventory/restock", json={"product_id": product_id, "quantity": 10, "reference": "REF"})
    
    # 2. Reserve stock
    response = client.post("/inventory/reserve", json={"product_id": product_id, "quantity": 5})
    reservation_id = response.json()["id"]
    
    # 3. Release reservation
    response = client.delete(f"/inventory/reserve/{reservation_id}")
    assert response.status_code == 200
    
    # 4. Check inventory
    response = client.get(f"/inventory/product/{product_id}")
    inventory = response.json()
    assert inventory["quantity_available"] == 10
    assert inventory["quantity_reserved"] == 0

def test_adjust_stock_endpoint(client):
    # 1. Create and restock product
    response = client.post("/products/", json={"name": "Test Product 4", "price": 40.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    client.post("/inventory/restock", json={"product_id": product_id, "quantity": 10, "reference": "REF"})
    
    # 2. Adjust stock
    response = client.post("/inventory/adjust", json={
        "product_id": product_id,
        "quantity": -2,
        "reason": "Damaged"
    })
    assert response.status_code == 200
    
    # 3. Check inventory
    response = client.get(f"/inventory/product/{product_id}")
    inventory = response.json()
    assert inventory["quantity_available"] == 8

def test_get_movements_endpoint(client):
    # 1. Create and restock product
    response = client.post("/products/", json={"name": "Test Product 5", "price": 50.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    client.post("/inventory/restock", json={"product_id": product_id, "quantity": 10, "reference": "REF"})
    
    # 2. Get movements
    response = client.get("/inventory/movements")
    assert response.status_code == 200
    movements = response.json()
    assert len(movements) >= 1
    assert movements[-1]["movement_type"] == "restock"

def test_low_stock_endpoint(client):
    # 1. Create and restock product with low stock
    response = client.post("/products/", json={"name": "Low Stock Product", "price": 5.0})
    assert response.status_code == 201
    product_id = response.json()["id"]
    # Default reorder_point is 10. Restock with 5.
    client.post("/inventory/restock", json={"product_id": product_id, "quantity": 5, "reference": "REF"})
    
    # Check inventory
    response = client.get(f"/inventory/product/{product_id}")
    print(f"Inventory: {response.json()}")
    
    # 2. Get low stock products
    response = client.get("/inventory/low-stock")
    assert response.status_code == 200
    low_stock = response.json()
    print(f"Low stock: {low_stock}")
    assert any(item["product_id"] == product_id for item in low_stock)
