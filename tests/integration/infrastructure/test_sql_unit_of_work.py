import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Inventory, Product
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.infrastructure.inventory.persistence.sql_unit_of_work import SqlUnitOfWork
from datetime import datetime

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    product2 = Product(id=2, name="Test Product 2", price=10.0)
    product3 = Product(id=3, name="Test Product 3", price=10.0)
    session.add_all([product2, product3])
    session.commit()
    
    yield session
    session.close()

def test_sql_unit_of_work_commit(db_session):
    uow = SqlUnitOfWork(db_session)
    with uow:
        inventory = DomainInventory(
            product_id=2,
            quantity_available=50,
            quantity_reserved=0,
            quantity_sold=0,
            reorder_point=5,
            version=1,
            last_restocked_at=datetime.utcnow()
        )
        uow.inventory_repo.save(inventory)
    
    # After 'with', it should be committed
    retrieved = db_session.query(Inventory).filter_by(product_id=2).first()
    assert retrieved is not None
    assert retrieved.quantity_available == 50

def test_sql_unit_of_work_rollback(db_session):
    uow = SqlUnitOfWork(db_session)
    try:
        with uow:
            inventory = DomainInventory(
                product_id=3,
                quantity_available=50,
                quantity_reserved=0,
                quantity_sold=0,
                reorder_point=5,
                version=1,
                last_restocked_at=datetime.utcnow()
            )
            uow.inventory_repo.save(inventory)
            raise Exception("Force rollback")
    except:
        pass
    
    # Should not be in DB
    retrieved = db_session.query(Inventory).filter_by(product_id=3).first()
    assert retrieved is None
