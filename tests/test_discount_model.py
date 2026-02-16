from datetime import datetime, timedelta
from app.models import Discount
from app.schemas import DiscountCreate

def test_create_discount_model(db):
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    
    assert discount.id is not None
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"
    assert discount.discount_value == 20.0

def test_discount_schema_validation():
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow(),
        "valid_until": datetime.utcnow() + timedelta(days=30),
        "is_active": True
    }
    discount_create = DiscountCreate(**discount_data)
    assert discount_create.code == "SUMMER2024"
