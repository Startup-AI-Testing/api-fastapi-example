import pytest
from datetime import datetime, timedelta
from app.models import Discount
from app.services.discount_service import DiscountService
from fastapi import HTTPException

def test_validate_discount_success():
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=5,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    # Should not raise exception
    DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_inactive():
    discount = Discount(
        code="INACTIVE",
        is_active=False,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(discount, 150.0)
    assert excinfo.value.status_code == 400
    assert "inactive" in excinfo.value.detail.lower()

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(discount, 150.0)
    assert excinfo.value.status_code == 400
    assert "expired" in excinfo.value.detail.lower()

def test_validate_discount_no_uses_left():
    discount = Discount(
        code="NOUSES",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=10
    )
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(discount, 150.0)
    assert excinfo.value.status_code == 400
    assert "no uses left" in excinfo.value.detail.lower()

def test_validate_discount_min_amount_not_reached():
    discount = Discount(
        code="MINAMOUNT",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0,
        min_order_amount=200.0
    )
    
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount(discount, 150.0)
    assert excinfo.value.status_code == 400
    assert "minimum order amount" in excinfo.value.detail.lower()

def test_calculate_discount_percentage():
    discount = Discount(
        discount_type="percentage",
        discount_value=20.0
    )
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 20.0

def test_calculate_discount_fixed_amount():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=15.0
    )
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 15.0

def test_calculate_discount_fixed_amount_more_than_total():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=150.0
    )
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 100.0
