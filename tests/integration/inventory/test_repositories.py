import pytest
import uuid
from datetime import datetime, timedelta
from app.models import Product, Inventory as InventoryModel
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.persistence.inventory.sql_stock_movement_repository import SqlStockMovementRepository

from src.domain.inventory.errors.inventory_errors import ConcurrencyError

def test_save_and_get_inventory(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    repo = SqlInventoryRepository(db)
    inventory = Inventory.create(product_id=product.id, quantity_available=100)
    
    # Act
    repo.save(inventory)
    retrieved = repo.get_by_product_id(product.id)
    
    # Assert
    assert retrieved is not None
    assert retrieved.product_id == product.id
    assert retrieved.quantity_available == 100
    assert retrieved.version == 1

def test_update_inventory_optimistic_locking(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    repo = SqlInventoryRepository(db)
    inventory = Inventory.create(product_id=product.id, quantity_available=100)
    repo.save(inventory)
    
    # Act
    inventory.reserve(10)
    repo.save(inventory)
    
    # Assert
    retrieved = repo.get_by_product_id(product.id)
    assert retrieved.quantity_available == 90
    assert retrieved.quantity_reserved == 10
    assert retrieved.version == 2

def test_optimistic_locking_failure(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    repo = SqlInventoryRepository(db)
    inventory = Inventory.create(product_id=product.id, quantity_available=100)
    repo.save(inventory)
    
    # Simulate two instances of the same version
    instance1 = repo.get_by_product_id(product.id)
    instance2 = repo.get_by_product_id(product.id)
    
    # Act
    instance1.reserve(10)
    repo.save(instance1) # version becomes 2
    
    instance2.reserve(5)
    with pytest.raises(ConcurrencyError):
        repo.save(instance2)

def test_save_and_get_reservation(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    inv_model = InventoryModel(product_id=product.id, quantity_available=100)
    db.add(inv_model)
    db.commit()
    
    repo = SqlStockReservationRepository(db)
    res_id = uuid.uuid4()
    reservation = StockReservation.create(
        id=res_id,
        inventory_id=product.id,
        quantity=5
    )
    
    # Act
    repo.save(reservation)
    retrieved = repo.get_by_id(res_id)
    
    # Assert
    assert retrieved is not None
    assert retrieved.id == res_id
    assert retrieved.quantity == 5
    assert retrieved.status == "active"

def test_list_expired_reservations(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    inv_model = InventoryModel(product_id=product.id, quantity_available=100)
    db.add(inv_model)
    db.commit()
    
    repo = SqlStockReservationRepository(db)
    
    # Active reservation
    res1 = StockReservation.create(id=uuid.uuid4(), inventory_id=product.id, quantity=5)
    repo.save(res1)
    
    # Expired reservation
    res2 = StockReservation.create(id=uuid.uuid4(), inventory_id=product.id, quantity=5)
    res2.expires_at = datetime.utcnow() - timedelta(minutes=1)
    repo.save(res2)
    
    # Act
    expired = repo.get_expired_reservations()
    
    # Assert
    assert len(expired) == 1
    assert expired[0].id == res2.id

def test_save_and_list_movements(db):
    # Arrange
    product = Product(name="Test Product", price=10.0, stock=0)
    db.add(product)
    db.commit()
    
    inv_model = InventoryModel(product_id=product.id, quantity_available=100)
    db.add(inv_model)
    db.commit()
    
    repo = SqlStockMovementRepository(db)
    movement = StockMovement.create(
        id=uuid.uuid4(),
        inventory_id=product.id,
        movement_type="restock",
        quantity=100
    )
    
    # Act
    repo.save(movement)
    movements = repo.get_by_inventory_id(product.id)
    
    # Assert
    assert len(movements) == 1
    assert movements[0].movement_type == "restock"
    assert movements[0].quantity == 100
