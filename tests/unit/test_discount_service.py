import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.discount_service import DiscountService
from app.models import Discount
from fastapi import HTTPException

def test_validate_discount_success():
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=Decimal("20.0"),
        min_order_amount=Decimal("100.0"),
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    # Should not raise exception
    DiscountService.validate_discount_object(discount, Decimal("150.0"))

def test_validate_discount_inactive():
    discount = Discount(code="TEST", is_active=False)
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount_object(discount, Decimal("150.0"))
    assert excinfo.value.status_code == 400
    assert "inactive" in excinfo.value.detail

def test_validate_discount_expired():
    discount = Discount(
        code="TEST",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount_object(discount, Decimal("150.0"))
    assert excinfo.value.status_code == 400
    assert "expired" in excinfo.value.detail

def test_validate_discount_no_uses_left():
    discount = Discount(
        code="TEST",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=10
    )
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount_object(discount, Decimal("150.0"))
    assert excinfo.value.status_code == 400
    assert "maximum uses" in excinfo.value.detail

def test_validate_discount_min_amount_not_met():
    discount = Discount(
        code="TEST",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0,
        min_order_amount=Decimal("200.0")
    )
    with pytest.raises(HTTPException) as excinfo:
        DiscountService.validate_discount_object(discount, Decimal("150.0"))
    assert excinfo.value.status_code == 400
    assert "Minimum order amount" in excinfo.value.detail

def test_calculate_discount_percentage():
    discount = Discount(
        discount_type="percentage",
        discount_value=Decimal("20.0")
    )
    amount = DiscountService.calculate_discount(discount, Decimal("100.0"))
    assert amount == Decimal("20.0")

def test_calculate_discount_fixed():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=Decimal("15.0")
    )
    amount = DiscountService.calculate_discount(discount, Decimal("100.0"))
    assert amount == Decimal("15.0")

def test_calculate_discount_fixed_more_than_total():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=Decimal("150.0")
    )
    amount = DiscountService.calculate_discount(discount, Decimal("100.0"))
    assert amount == Decimal("100.0")
