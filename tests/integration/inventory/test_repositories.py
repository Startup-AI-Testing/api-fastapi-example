import pytest
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainReservation
from src.domain.inventory.entities.stock_movement import StockMovement as DomainMovement
from app import models

def test_inventory_repository_save_and_get(db):
    # Create product first
    product = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(product)
    db.commit()
    
    repo = SqlInventoryRepository(db)
    domain_inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    
    repo.save(domain_inventory)
    db.commit()
    
    saved_inventory = repo.get_by_product_id(product.id)
    assert saved_inventory.product_id == product.id
    assert saved_inventory.quantity_available == 10
    assert saved_inventory.version == 1

def test_inventory_repository_optimistic_locking(db):
    # Create product first
    product = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(product)
    db.commit()
    
    repo = SqlInventoryRepository(db)
    domain_inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    repo.save(domain_inventory)
    db.commit()
    
    # Simulate two concurrent updates
    inventory_v1_a = repo.get_by_product_id(product.id)
    inventory_v1_b = repo.get_by_product_id(product.id)
    
    inventory_v1_a.reserve_stock(2)
    repo.save(inventory_v1_a)
    db.commit()
    
    inventory_v1_b.reserve_stock(3)
    with pytest.raises(Exception, match="Concurrency conflict"):
        repo.save(inventory_v1_b)

def test_reservation_repository_save_and_get(db):
    # Setup
    product = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(product)
    db.commit()
    
    inv_repo = SqlInventoryRepository(db)
    domain_inventory = DomainInventory.create(product_id=product.id, quantity_available=10)
    inv_repo.save(domain_inventory)
    db.commit()
    
    res_repo = SqlStockReservationRepository(db)
    domain_res = DomainReservation.create(inventory_id=product.id, quantity=2)
    
    res_repo.save(domain_res)
    db.commit()
    
    saved_res = res_repo.get_by_id(domain_res.id)
    assert saved_res.id == domain_res.id
    assert saved_res.quantity == 2
    assert saved_res.status == "active"
