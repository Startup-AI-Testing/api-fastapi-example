import pytest
from app import models

def test_create_order_with_reservation(client, db):
    # Create product and inventory
    product = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(product)
    db.commit()
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    # Reserve stock
    res_resp = client.post("/inventory/reserve", json={
        "product_id": product.id,
        "quantity": 2
    })
    reservation_id = res_resp.json()["id"]

    # Create order
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": product.id, "quantity": 2}],
        "reservation_id": reservation_id
    }
    response = client.post("/orders/", json=order_data)
    
    assert response.status_code == 201
    
    # Verify inventory
    inv_resp = client.get(f"/inventory/product/{product.id}")
    assert inv_resp.json()["quantity_available"] == 8
    assert inv_resp.json()["quantity_reserved"] == 0
    assert inv_resp.json()["quantity_sold"] == 2
    
    # Verify reservation status
    # We don't have an endpoint to get reservation by ID but we can check DB
    from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
    res_repo = SqlStockReservationRepository(db)
    from uuid import UUID
    reservation = res_repo.get_by_id(UUID(reservation_id))
    assert reservation.status == "confirmed"
    assert reservation.order_id is not None
