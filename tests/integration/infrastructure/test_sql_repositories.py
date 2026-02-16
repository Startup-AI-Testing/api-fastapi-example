import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Inventory, StockReservation, StockMovement, Product
from src.infrastructure.inventory.persistence.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.inventory.persistence.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.inventory.persistence.sql_stock_movement_repository import SqlStockMovementRepository
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainStockReservation
from src.domain.inventory.entities.stock_movement import StockMovement as DomainStockMovement
from uuid import uuid4
from datetime import datetime, timedelta

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add a product for FK constraints (though SQLite might not enforce them by default, it's good practice)
    product = Product(id=1, name="Test Product", price=10.0)
    session.add(product)
    session.commit()
    
    yield session
    session.close()

def test_sql_inventory_repository_save_and_get(db_session):
    repo = SqlInventoryRepository(db_session)
    domain_inventory = DomainInventory(
        product_id=1,
        quantity_available=100,
        quantity_reserved=0,
        quantity_sold=0,
        reorder_point=10,
        version=1,
        last_restocked_at=datetime.utcnow()
    )
    
    repo.save(domain_inventory)
    db_session.commit()
    
    retrieved = repo.get_by_product_id(1)
    assert retrieved is not None
    assert retrieved.product_id == 1
    assert retrieved.quantity_available == 100

def test_sql_stock_reservation_repository_save_and_get(db_session):
    # Need inventory first
    db_session.add(Inventory(product_id=1, quantity_available=100, quantity_reserved=0, quantity_sold=0, reorder_point=10, version=1))
    db_session.commit()
    
    repo = SqlStockReservationRepository(db_session)
    res_id = uuid4()
    domain_res = DomainStockReservation(
        id=res_id,
        inventory_id=1,
        order_id=None,
        quantity=5,
        reserved_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        status="active",
        reservation_type="order"
    )
    
    repo.save(domain_res)
    db_session.commit()
    
    retrieved = repo.get_by_id(res_id)
    assert retrieved is not None
    assert retrieved.id == res_id
    assert retrieved.quantity == 5

def test_sql_stock_movement_repository_save(db_session):
    db_session.add(Inventory(product_id=1, quantity_available=100, quantity_reserved=0, quantity_sold=0, reorder_point=10, version=1))
    db_session.commit()
    
    repo = SqlStockMovementRepository(db_session)
    domain_mov = DomainStockMovement.create(
        inventory_id=1,
        movement_type="restock",
        quantity=50,
        created_by="admin"
    )
    
    repo.save(domain_mov)
    db_session.commit()
    
    # Verify in DB directly
    mov = db_session.query(StockMovement).filter_by(id=str(domain_mov.id)).first()
    assert mov is not None
    assert mov.quantity == 50
