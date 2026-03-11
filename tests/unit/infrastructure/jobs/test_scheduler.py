import pytest
from sqlalchemy.orm import Session
from app import models
from src.infrastructure.jobs.scheduler import release_expired_reservations_job
from datetime import datetime, timedelta
import uuid

def test_release_expired_reservations_job(db: Session):
    # 1. Create a product and inventory
    product = models.Product(name="Job Test Product", price=10.0, stock=10)
    db.add(product)
    db.commit()
    
    inventory = models.Inventory(
        product_id=product.id,
        quantity_available=8,
        quantity_reserved=2,
        quantity_sold=0
    )
    db.add(inventory)
    db.commit()
    
    # 2. Create an expired reservation
    expired_res = models.StockReservation(
        id=uuid.uuid4(),
        inventory_id=product.id,
        quantity=2,
        reserved_at=datetime.utcnow() - timedelta(minutes=20),
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        status="active",
        reservation_type="cart"
    )
    db.add(expired_res)
    db.commit()
    
    # 3. Run the job
    # We need to make sure the job uses our test DB.
    # Since the job uses SessionLocal from app.database, we might need to override it.
    # But for a simple test, we can just call the service method directly if we want.
    # To test the job itself, we'd need to mock SessionLocal.
    
    from unittest.mock import patch
    with patch("src.infrastructure.jobs.scheduler.SessionLocal", return_value=db):
        # Prevent the job from closing the test session
        with patch.object(db, 'close'):
            release_expired_reservations_job()
    
    # 4. Verify results
    db.refresh(expired_res)
    assert expired_res.status == "released"
    
    db.refresh(inventory)
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0
