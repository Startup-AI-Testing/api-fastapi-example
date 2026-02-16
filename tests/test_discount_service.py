import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from sqlalchemy.orm import Session
from fastapi import HTTPException

def test_validate_valid_discount(db: Session):
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = datetime.utcnow() + timedelta(days=1)
    
    discount = Discount(
        code="VALID",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        valid_from=valid_from,
        valid_until=valid_until,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    # Valid case
    discount_obj = DiscountService.validate_discount(db, "VALID", 100.0)
    assert discount_obj.code == "VALID"

def test_validate_inactive_discount(db: Session):
    discount = Discount(
        code="INACTIVE",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=False
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "INACTIVE", 100.0)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Discount is not active"

def test_validate_expired_discount(db: Session):
    discount = Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "EXPIRED", 100.0)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Discount has expired"

def test_validate_max_uses_reached(db: Session):
    discount = Discount(
        code="MAXED",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=5,
        current_uses=5,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "MAXED", 100.0)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Discount usage limit reached"

def test_validate_min_order_amount(db: Session):
    discount = Discount(
        code="MIN_ORDER",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=200.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "MIN_ORDER", 100.0)
    assert excinfo.value.status_code == 400
    assert "Order amount is less than minimum required" in excinfo.value.detail

def test_calculate_discount_percentage(db: Session):
    discount = Discount(
        code="PERCENT",
        discount_type="percentage",
        discount_value=20.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 20.0

def test_calculate_discount_fixed(db: Session):
    discount = Discount(
        code="FIXED",
        discount_type="fixed_amount",
        discount_value=15.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 15.0

def test_calculate_discount_fixed_more_than_total(db: Session):
    discount = Discount(
        code="FIXED_BIG",
        discount_type="fixed_amount",
        discount_value=150.0,
        max_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 100.0

