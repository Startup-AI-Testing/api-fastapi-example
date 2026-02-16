import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from fastapi import HTTPException

def test_calculate_discount_percentage():
    discount = Discount(
        code="SUMMER20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        is_active=True
    )
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 40.0

def test_calculate_discount_fixed():
    discount = Discount(
        code="FIXED50",
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=100.0,
        is_active=True
    )
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 50.0

def test_validate_discount_success():
    discount = Discount(
        code="VALID",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=50.0,
        is_active=True,
        max_uses=10,
        current_uses=5,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1)
    )
    # Should not raise exception
    DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_inactive():
    discount = Discount(code="INACTIVE", is_active=False)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "expired" in exc.value.detail

def test_validate_discount_max_uses():
    discount = Discount(
        code="MAXED",
        is_active=True,
        max_uses=10,
        current_uses=10
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "limit" in exc.value.detail

def test_validate_discount_min_amount():
    discount = Discount(
        code="MIN",
        is_active=True,
        min_order_amount=100.0
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 50.0)
    assert exc.value.status_code == 400
    assert "minimum" in exc.value.detail
