import pytest
from datetime import datetime, timedelta
from app import models
from src.infrastructure.jobs.inventory_jobs import release_expired_reservations_job

def test_release_expired_reservations_job(db):
    # 1. Setup inventory
    product = models.Product(name="Job Product", price=10.0, stock=10)
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
    
    # 2. Create an expired reservation
    import uuid
    expired_res = models.StockReservation(
        id=str(uuid.uuid4()),
        inventory_id=inventory.product_id,
        quantity=3,
        reserved_at=datetime.utcnow() - timedelta(minutes=20),
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        status="active",
        reservation_type="cart"
    )
    # Manually update inventory to reflect reservation
    inventory.quantity_available -= 3
    inventory.quantity_reserved += 3
    
    db.add(expired_res)
    db.commit()
    
    # 3. Create an active (not expired) reservation
    active_res = models.StockReservation(
        id=str(uuid.uuid4()),
        inventory_id=inventory.product_id,
        quantity=2,
        reserved_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        status="active",
        reservation_type="cart"
    )
    inventory.quantity_available -= 2
    inventory.quantity_reserved += 2
    db.add(active_res)
    db.commit()
    
    # Verify initial state
    db.refresh(inventory)
    assert inventory.quantity_available == 5
    assert inventory.quantity_reserved == 5
    
    # 4. Run the job
    release_expired_reservations_job(db)
    
    # 5. Verify results
    db.refresh(inventory)
    # Expired (3) should be released, Active (2) should remain
    # quantity_available: 5 + 3 = 8
    # quantity_reserved: 5 - 3 = 2
    assert inventory.quantity_available == 8
    assert inventory.quantity_reserved == 2
    
    db.refresh(expired_res)
    assert expired_res.status == "released"
    
    db.refresh(active_res)
    assert active_res.status == "active"
