from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount

def test_validate_discount_success():
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    
    # Mocking order amount
    order_amount = 150.0
    
    is_valid, error = DiscountService.validate_discount(discount, order_amount)
    assert is_valid is True
    assert error is None

def test_validate_discount_inactive():
    discount = Discount(
        code="SUMMER2024",
        is_active=False
    )
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount is not active"

def test_validate_discount_expired():
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount has expired"

def test_validate_discount_not_started():
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        valid_from=datetime.utcnow() + timedelta(days=1)
    )
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount is not yet valid"

def test_validate_discount_max_uses():
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        max_uses=10,
        current_uses=10
    )
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount has reached maximum uses"

def test_validate_discount_min_amount():
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        min_order_amount=200.0
    )
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Order amount is below minimum required for this discount"

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

def test_calculate_discount_fixed_more_than_total():
    discount = Discount(
        discount_type="fixed_amount",
        discount_value=150.0
    )
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 100.0
