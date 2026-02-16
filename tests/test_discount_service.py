import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount
from app.errors import DiscountError

def test_validate_percentage_discount():
    discount = Discount(
        code="SUMMER20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    # Valid case
    discount_amount = DiscountService.validate_and_calculate(discount, 150.0)
    assert discount_amount == 30.0

def test_validate_fixed_amount_discount():
    discount = Discount(
        code="FIXED50",
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=200.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    # Valid case
    discount_amount = DiscountService.validate_and_calculate(discount, 250.0)
    assert discount_amount == 50.0

def test_discount_inactive():
    discount = Discount(is_active=False)
    with pytest.raises(DiscountError, match="Discount is not active"):
        DiscountService.validate_and_calculate(discount, 100.0)

def test_discount_expired():
    discount = Discount(
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(DiscountError, match="Discount is expired"):
        DiscountService.validate_and_calculate(discount, 100.0)

def test_discount_not_yet_valid():
    discount = Discount(
        is_active=True,
        valid_from=datetime.utcnow() + timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=10)
    )
    with pytest.raises(DiscountError, match="Discount is not yet valid"):
        DiscountService.validate_and_calculate(discount, 100.0)

def test_discount_max_uses_reached():
    discount = Discount(
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=10
    )
    with pytest.raises(DiscountError, match="Discount usage limit reached"):
        DiscountService.validate_and_calculate(discount, 100.0)

def test_discount_min_amount_not_met():
    discount = Discount(
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0
    )
    with pytest.raises(DiscountError, match="Minimum order amount not met"):
        DiscountService.validate_and_calculate(discount, 50.0)
