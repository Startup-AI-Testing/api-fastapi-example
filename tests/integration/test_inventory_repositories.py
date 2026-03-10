import pytest
from sqlalchemy.orm import Session
from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository, SqlStockReservationRepository
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainReservation
from app.models import Product
import uuid
from datetime import datetime, timedelta

@pytest.fixture
def product(db: Session):
    p = Product(name="Test Product", price=10.0, stock=10)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def test_inventory_repository_save_and_get(db: Session, product):
    repo = SqlInventoryRepository(db)
    inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    repo.save(inventory)
    
    fetched = repo.get_by_product_id(product.id)
    assert fetched.product_id == product.id
    assert fetched.quantity_available == 10
    assert fetched.version == 1

def test_inventory_repository_optimistic_locking(db: Session, product):
    repo = SqlInventoryRepository(db)
    inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    repo.save(inventory)
    
    # Simulate two concurrent updates
    inv1 = repo.get_by_product_id(product.id)
    inv2 = repo.get_by_product_id(product.id)
    
    inv1.reserve(2)
    repo.save(inv1) # Success, version becomes 2
    
    inv2.reserve(3)
    with pytest.raises(Exception, match="Concurrency conflict"):
        repo.save(inv2) # Should fail because version is still 1 in inv2

def test_stock_reservation_repository_save_and_get(db: Session, product):
    # First create inventory
    inv_repo = SqlInventoryRepository(db)
    inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    inv_repo.save(inventory)
    
    res_repo = SqlStockReservationRepository(db)
    reservation = DomainReservation.create(inventory_id=product.id, quantity=2)
    res_repo.save(reservation)
    
    fetched = res_repo.get_by_id(reservation.id)
    assert fetched.id == reservation.id
    assert fetched.quantity == 2
    assert fetched.status == "active"
