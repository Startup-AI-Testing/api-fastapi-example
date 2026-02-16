from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Discount, Order

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_discount(db):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=valid_from,
        valid_until=valid_until,
        is_active=True
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    
    assert discount.id is not None
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"
    assert discount.discount_value == 20.0
    assert discount.min_order_amount == 100.0
    assert discount.max_uses == 10
    assert discount.current_uses == 0
    assert discount.is_active is True

def test_order_with_discount_fields(db):
    order = Order(
        customer_name="John Doe",
        customer_email="john@example.com",
        discount_code="SUMMER2024",
        discount_amount=20.0,
        subtotal=100.0,
        total=80.0
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    assert order.discount_code == "SUMMER2024"
    assert order.discount_amount == 20.0
    assert order.subtotal == 100.0
    assert order.total == 80.0
