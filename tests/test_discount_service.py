import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from app.errors import DiscountError

def test_calculate_discount_percentage():
    discount = Discount(
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 40.0

def test_calculate_discount_fixed():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 50.0

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_from=datetime.now() - timedelta(days=2),
        valid_until=datetime.now() - timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    with pytest.raises(DiscountError, match="Discount code has expired"):
        DiscountService.validate_discount(discount, 200.0)

def test_validate_discount_inactive():
    discount = Discount(
        code="INACTIVE",
        is_active=False,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    with pytest.raises(DiscountError, match="Discount code is not active"):
        DiscountService.validate_discount(discount, 200.0)

def test_validate_discount_max_uses():
    discount = Discount(
        code="MAX_USES",
        is_active=True,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        max_uses=10,
        current_uses=10
    )
    with pytest.raises(DiscountError, match="Discount code has reached its maximum uses"):
        DiscountService.validate_discount(discount, 200.0)

def test_validate_discount_min_amount():
    discount = Discount(
        code="MIN_AMOUNT",
        is_active=True,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        max_uses=10,
        current_uses=0,
        min_order_amount=500.0
    )
    with pytest.raises(DiscountError, match="Order amount is below the minimum required"):
        DiscountService.validate_discount(discount, 200.0)
