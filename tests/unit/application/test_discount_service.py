import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount

@pytest.fixture
def active_percentage_discount():
    return Discount(
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

@pytest.fixture
def active_fixed_discount():
    return Discount(
        code="FIXED50",
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=200.0,
        max_uses=5,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )

def test_validate_discount_success(active_percentage_discount):
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 150.0)
    assert is_valid is True
    assert error is None

def test_validate_discount_inactive(active_percentage_discount):
    active_percentage_discount.is_active = False
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 150.0)
    assert is_valid is False
    assert error == "Discount is not active"

def test_validate_discount_expired(active_percentage_discount):
    active_percentage_discount.valid_until = datetime.utcnow() - timedelta(days=1)
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 150.0)
    assert is_valid is False
    assert error == "Discount has expired"

def test_validate_discount_not_started(active_percentage_discount):
    active_percentage_discount.valid_from = datetime.utcnow() + timedelta(days=1)
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 150.0)
    assert is_valid is False
    assert error == "Discount is not yet valid"

def test_validate_discount_no_uses_left(active_percentage_discount):
    active_percentage_discount.current_uses = 10
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 150.0)
    assert is_valid is False
    assert error == "Discount has reached its maximum uses"

def test_validate_discount_min_amount_not_met(active_percentage_discount):
    is_valid, error = DiscountService.validate_discount(active_percentage_discount, 50.0)
    assert is_valid is False
    assert error == "Order amount is below the minimum required for this discount"

def test_calculate_discount_percentage(active_percentage_discount):
    amount = DiscountService.calculate_discount_amount(active_percentage_discount, 200.0)
    assert amount == 40.0

def test_calculate_discount_fixed(active_fixed_discount):
    amount = DiscountService.calculate_discount_amount(active_fixed_discount, 300.0)
    assert amount == 50.0

def test_calculate_discount_fixed_more_than_total(active_fixed_discount):
    # If discount is 50 but total is 40, discount should be 40 (or 50 but total becomes 0)
    # Usually it's capped at total.
    amount = DiscountService.calculate_discount_amount(active_fixed_discount, 40.0)
    assert amount == 40.0
