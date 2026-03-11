import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app import models
import uuid

def test_order_creation_with_reservation(client: TestClient, db: Session):
    # 1. Create a product
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # 2. Initialize inventory
    restock_response = client.post("/inventory/restock", json={"product_id": product.id, "quantity": 100, "reference": "initial_stock"})
    if restock_response.status_code != 200:
        print(f"Restock failed: {restock_response.json()}")
    assert restock_response.status_code == 200
    
    # 3. Create a reservation
    res_response = client.post("/inventory/reserve", json={"product_id": product.id, "quantity": 2})
    if res_response.status_code != 200:
        print(f"Reservation failed for product {product.id}: {res_response.json()}")
    assert res_response.status_code == 200
    reservation_id = res_response.json()["id"]
    
    # Verify inventory state
    inv_response = client.get(f"/inventory/product/{product.id}")
    assert inv_response.json()["quantity_available"] == 98
    assert inv_response.json()["quantity_reserved"] == 2
    
    # 4. Create an order using the reservation
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 2}],
        "reservation_ids": [reservation_id]
    }
    order_response = client.post("/orders/", json=order_data)
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # 5. Verify inventory state after order
    inv_response = client.get(f"/inventory/product/{product.id}")
    assert inv_response.json()["quantity_available"] == 98
    assert inv_response.json()["quantity_reserved"] == 0
    assert inv_response.json()["quantity_sold"] == 2
    
    # Verify Product.stock is also updated
    db.refresh(product)
    assert product.stock == 98
    
    # 6. Cancel the order
    del_response = client.delete(f"/orders/{order_id}")
    assert del_response.status_code == 204
    
    # 7. Verify inventory state after cancellation
    inv_response = client.get(f"/inventory/product/{product.id}")
    assert inv_response.json()["quantity_available"] == 100
    assert inv_response.json()["quantity_reserved"] == 0
    assert inv_response.json()["quantity_sold"] == 0
    
    # Verify Product.stock is restored
    db.refresh(product)
    assert product.stock == 100

def test_order_creation_fails_with_invalid_reservation(client: TestClient, db: Session):
    # 1. Create a product
    product = models.Product(name="Test Product 2", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    # 2. Try to create an order with a non-existent reservation
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 2}],
        "reservation_ids": [str(uuid.uuid4())]
    }
    order_response = client.post("/orders/", json=order_data)
    assert order_response.status_code == 400
    assert "not found" in order_response.json()["detail"]
