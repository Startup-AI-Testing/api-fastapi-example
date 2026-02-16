import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.persistence.inventory.sql_stock_movement_repository import SqlStockMovementRepository
import uuid

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # We need to import the ORM models so they are registered with Base
    from src.infrastructure.persistence.inventory.orm_models import InventoryORM, StockReservationORM, StockMovementORM
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_inventory_repository_save_and_get(db_session):
    repo = SqlInventoryRepository(db_session)
    inventory = Inventory.create(product_id=1, quantity_available=100, reorder_point=10)
    
    repo.save(inventory)
    
    saved_inventory = repo.get_by_product_id(1)
    assert saved_inventory is not None
    assert saved_inventory.product_id == 1
    assert saved_inventory.quantity_available == 100
    assert saved_inventory.id is not None

def test_inventory_repository_optimistic_locking(db_session):
    repo = SqlInventoryRepository(db_session)
    inventory = Inventory.create(product_id=1, quantity_available=100)
    repo.save(inventory)
    
    # Simulate two concurrent sessions
    inv1 = repo.get_by_product_id(1)
    inv2 = repo.get_by_product_id(1)
    
    inv1.quantity_available = 90
    repo.save(inv1)
    
    inv2.quantity_available = 80
    with pytest.raises(Exception) as excinfo: # Should be a specific ConcurrencyError
        repo.save(inv2)
    
    assert "version" in str(excinfo.value).lower() or "conflict" in str(excinfo.value).lower()

def test_stock_reservation_repository_save_and_get(db_session):
    repo = SqlStockReservationRepository(db_session)
    reservation = StockReservation.create(
        inventory_id=1,
        quantity=5,
        reservation_type="order"
    )
    
    repo.save(reservation)
    
    saved_reservation = repo.get_by_id(reservation.id)
    assert saved_reservation is not None
    assert saved_reservation.id == reservation.id
    assert saved_reservation.quantity == 5

def test_stock_movement_repository_save(db_session):
    repo = SqlStockMovementRepository(db_session)
    movement = StockMovement.create(
        inventory_id=1,
        movement_type="restock",
        quantity=50
    )
    
    repo.save(movement)
    # If no exception, it's fine for now as it's an audit log
