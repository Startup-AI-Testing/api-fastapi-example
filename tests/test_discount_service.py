import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from fastapi import HTTPException

def test_calculate_percentage_discount():
    discount = Discount(discount_type="percentage", discount_value=20.0)
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 20.0

def test_calculate_fixed_amount_discount():
    discount = Discount(discount_type="fixed_amount", discount_value=15.0)
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 15.0

def test_validate_discount_success():
    discount = Discount(
        code="SUMMER2024",
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
    discount = Discount(code="OFF", is_active=False)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail

def test_validate_discount_expired():
    discount = Discount(
        code="OLD",
        is_active=True,
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "expired" in exc.value.detail

def test_validate_discount_no_uses():
    discount = Discount(
        code="FULL",
        is_active=True,
        max_uses=10,
        current_uses=10
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "limit reached" in exc.value.detail

def test_validate_discount_min_amount():
    discount = Discount(
        code="BIG",
        is_active=True,
        min_order_amount=200.0
    )
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 100.0)
    assert exc.value.status_code == 400
    assert "minimum amount" in exc.value.detail
