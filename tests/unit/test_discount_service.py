import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from fastapi import HTTPException

def test_validate_discount_success():
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = datetime.utcnow() + timedelta(days=1)
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
    
    # Should not raise exception
    DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_inactive():
    discount = Discount(code="INACTIVE", is_active=False)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 150.0)
    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail.lower()

def test_validate_discount_expired():
    valid_until = datetime.utcnow() - timedelta(days=1)
    discount = Discount(code="EXPIRED", is_active=True, valid_until=valid_until)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 150.0)
    assert exc.value.status_code == 400
    assert "expired" in exc.value.detail.lower()

def test_validate_discount_not_yet_valid():
    valid_from = datetime.utcnow() + timedelta(days=1)
    discount = Discount(code="FUTURE", is_active=True, valid_from=valid_from)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 150.0)
    assert exc.value.status_code == 400
    assert "not yet valid" in exc.value.detail.lower()

def test_validate_discount_max_uses():
    discount = Discount(code="MAX_USES", is_active=True, max_uses=10, current_uses=10)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 150.0)
    assert exc.value.status_code == 400
    assert "limit reached" in exc.value.detail.lower()

def test_validate_discount_min_amount():
    discount = Discount(code="MIN_AMOUNT", is_active=True, min_order_amount=100.0)
    with pytest.raises(HTTPException) as exc:
        DiscountService.validate_discount(discount, 50.0)
    assert exc.value.status_code == 400
    assert "minimum amount" in exc.value.detail.lower()

def test_calculate_discount_percentage():
    discount = Discount(discount_type="percentage", discount_value=20.0)
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 20.0

def test_calculate_discount_fixed():
    discount = Discount(discount_type="fixed_amount", discount_value=15.0)
    amount = DiscountService.calculate_discount(discount, 100.0)
    assert amount == 15.0
