import pytest
from uuid import UUID
from app import models

def test_create_order_with_reservation(client, db):
    # 1. Create product and inventory
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    
    inventory = models.Inventory(
        product_id=product.id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_sold=0,
        reorder_point=2,
        version=1
    )
    db.add(inventory)
    db.commit()
    
    # 2. Reserve stock
    reserve_payload = {
        "product_id": product.id,
        "quantity": 3,
        "reservation_type": "order"
    }
    response = client.post("/inventory/reserve", json=reserve_payload)
    assert response.status_code == 201
    reservation_id = response.json()["id"]
    
    # Verify inventory state
    db.refresh(inventory)
    assert inventory.quantity_available == 7
    assert inventory.quantity_reserved == 3
    
    # 3. Create order using the reservation
    order_payload = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": product.id, "quantity": 3}
        ],
        "reservation_id": reservation_id
    }
    response = client.post("/orders/", json=order_payload)
    assert response.status_code == 201
    order_id = response.json()["id"]
    
    # 4. Verify inventory state after order
    db.refresh(inventory)
    assert inventory.quantity_available == 7
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 3
    
    # Verify legacy stock
    db.refresh(product)
    assert product.stock == 7
    
    # Verify reservation status
    reservation_orm = db.query(models.StockReservation).filter(models.StockReservation.id == reservation_id).first()
    assert reservation_orm.status == "confirmed"
    assert str(reservation_orm.order_id) == str(order_id)

def test_delete_order_restores_stock(client, db):
    # 1. Setup product, inventory, reservation and order
    product = models.Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    
    inventory = models.Inventory(
        product_id=product.id,
        quantity_available=10,
        quantity_reserved=0,
        quantity_sold=0,
        reorder_point=2,
        version=1
    )
    db.add(inventory)
    db.commit()
    
    # Reserve and confirm via order
    reserve_response = client.post("/inventory/reserve", json={
        "product_id": product.id, "quantity": 2, "reservation_type": "order"
    })
    reservation_id = reserve_response.json()["id"]
    
    order_response = client.post("/orders/", json={
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "items": [{"product_id": product.id, "quantity": 2}],
        "reservation_id": reservation_id
    })
    order_id = order_response.json()["id"]
    
    # Verify state before deletion
    db.refresh(inventory)
    assert inventory.quantity_available == 8
    assert inventory.quantity_sold == 2
    db.refresh(product)
    assert product.stock == 8
    
    # 2. Delete order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204
    
    # 3. Verify stock restoration
    db.refresh(inventory)
    assert inventory.quantity_available == 10
    assert inventory.quantity_sold == 0
    db.refresh(product)
    assert product.stock == 10
    
    # Verify reservation status
    reservation_orm = db.query(models.StockReservation).filter(models.StockReservation.id == reservation_id).first()
    assert reservation_orm.status == "released"
