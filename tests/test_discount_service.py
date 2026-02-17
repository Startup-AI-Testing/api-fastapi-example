import pytest
from datetime import datetime, timedelta
from app.models import Discount
from app.services.discount_service import DiscountService

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
    discount = Discount(code="INACTIVE", is_active=False)
    with pytest.raises(ValueError, match="Discount is not active"):
        DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount has expired"):
        DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_not_started():
    discount = Discount(
        code="FUTURE",
        is_active=True,
        valid_from=datetime.utcnow() + timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount is not yet valid"):
        DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_no_uses_left():
    discount = Discount(
        code="USED_UP",
        is_active=True,
        max_uses=5,
        current_uses=5
    )
    with pytest.raises(ValueError, match="Discount usage limit reached"):
        DiscountService.validate_discount(discount, 100.0)

def test_validate_discount_min_amount():
    discount = Discount(
        code="MIN_100",
        is_active=True,
        min_order_amount=100.0
    )
    with pytest.raises(ValueError, match="Order amount is below the minimum required"):
        DiscountService.validate_discount(discount, 50.0)

def test_calculate_discount_percentage():
    discount = Discount(discount_type="percentage", discount_value=20.0)
    amount = DiscountService.calculate_discount_amount(discount, 200.0)
    assert amount == 40.0

def test_calculate_discount_fixed():
    discount = Discount(discount_type="fixed_amount", discount_value=50.0)
    amount = DiscountService.calculate_discount_amount(discount, 200.0)
    assert amount == 50.0

def test_calculate_discount_fixed_more_than_total():
    discount = Discount(discount_type="fixed_amount", discount_value=250.0)
    amount = DiscountService.calculate_discount_amount(discount, 200.0)
    assert amount == 200.0
