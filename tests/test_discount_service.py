import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from fastapi import HTTPException

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

def test_validate_discount_success():
    discount = Discount(
        code="VALID",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=5,
        min_order_amount=50.0
    )
    # Should not raise exception
    DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_inactive():
    discount = Discount(code="INACTIVE", is_active=False)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail.lower()

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(days=1),
        max_uses=10,
        current_uses=0,
        min_order_amount=0.0
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "expired" in exc.value.detail.lower()

def test_validate_discount_no_uses():
    discount = Discount(
        code="NOUSES",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=10,
        min_order_amount=0.0
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "no uses left" in exc.value.detail.lower()

def test_validate_discount_min_amount():
    discount = Discount(
        code="MINAMOUNT",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0,
        min_order_amount=100.0
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 50.0)
    assert exc.value.status_code == 400
    assert "minimum order amount" in exc.value.detail.lower()
