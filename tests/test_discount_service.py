import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount

def test_validate_discount_valid():
    discount = Discount(
        code="SUMMER20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    # Should not raise any exception
    DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_inactive():
    discount = Discount(
        code="INACTIVE",
        is_active=False,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount is not active"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_from=datetime.now() - timedelta(days=10),
        valid_until=datetime.now() - timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount has expired"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_not_yet_valid():
    discount = Discount(
        code="FUTURE",
        is_active=True,
        valid_from=datetime.now() + timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=10)
    )
    with pytest.raises(ValueError, match="Discount is not yet valid"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_max_uses_reached():
    discount = Discount(
        code="MAXED",
        is_active=True,
        max_uses=5,
        current_uses=5,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount usage limit reached"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_min_amount_not_met():
    discount = Discount(
        code="MIN100",
        is_active=True,
        min_order_amount=100.0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Order amount does not meet minimum requirement"):
        DiscountService.validate_discount(discount, 50.0)

def test_calculate_discount_percentage():
    discount = Discount(
        discount_type="percentage",
        discount_value=20.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 200.0)
    assert amount == 40.0

def test_calculate_discount_fixed():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=50.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 200.0)
    assert amount == 50.0

def test_calculate_discount_fixed_capped():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=100.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 50.0)
    assert amount == 50.0
