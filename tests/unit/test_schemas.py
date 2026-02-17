from datetime import datetime, timedelta
from app.schemas import DiscountCreate, Discount

def test_discount_create_schema():
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow(),
        "valid_until": datetime.utcnow() + timedelta(days=30),
        "is_active": True
    }
    discount_in = DiscountCreate(**data)
    assert discount_in.code == "SUMMER2024"

def test_discount_schema_from_orm():
    now = datetime.utcnow()
    data = {
        "id": 1,
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "current_uses": 0,
        "valid_from": now,
        "valid_until": now + timedelta(days=30),
        "is_active": True
    }
    # Mocking an ORM object
    class MockORM:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    mock_discount = MockORM(**data)
    discount_out = Discount.from_orm(mock_discount)
    assert discount_out.id == 1
    assert discount_out.code == "SUMMER2024"
