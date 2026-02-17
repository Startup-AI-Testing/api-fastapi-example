import pytest
from datetime import datetime, timedelta
from app.models import Discount
from app.services.discount_service import DiscountService
from fastapi import HTTPException

def test_validate_discount_success(db):
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    validated_discount = DiscountService.validate_discount(db, "SUMMER2024", 150.0)
    assert validated_discount.code == "SUMMER2024"

def test_validate_discount_not_found(db):
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "NONEXISTENT", 150.0)
    assert excinfo.value.status_code == 404

def test_validate_discount_inactive(db):
    discount = Discount(
        code="INACTIVE",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=False
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "INACTIVE", 150.0)
    assert excinfo.value.status_code == 400
    assert "inactive" in excinfo.value.detail.lower()

def test_validate_discount_expired(db):
    discount = Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "EXPIRED", 150.0)
    assert excinfo.value.status_code == 400
    assert "expired" in excinfo.value.detail.lower()

def test_validate_discount_no_uses_left(db):
    discount = Discount(
        code="NOUSES",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "NOUSES", 150.0)
    assert excinfo.value.status_code == 400
    assert "uses" in excinfo.value.detail.lower()

def test_validate_discount_min_amount(db):
    discount = Discount(
        code="MINAMOUNT",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(db, "MINAMOUNT", 50.0)
    assert excinfo.value.status_code == 400
    assert "minimum" in excinfo.value.detail.lower()

def test_calculate_discount_percentage():
    discount = Discount(
        discount_type="percentage",
        discount_value=20.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 20.0

def test_calculate_discount_fixed():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=15.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 15.0

def test_calculate_discount_fixed_more_than_total():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=150.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 100.0
