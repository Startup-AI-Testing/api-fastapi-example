from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount

def test_validate_discount_active():
    now = datetime.utcnow()
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
        is_active=True
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is True
    assert amount == 30.0
    assert msg is None

def test_validate_discount_inactive():
    now = datetime.utcnow()
    discount = Discount(
        code="SUMMER2024",
        is_active=False,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert msg == "Discount is not active"

def test_validate_discount_expired():
    now = datetime.utcnow()
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        valid_from=now - timedelta(days=10),
        valid_until=now - timedelta(days=1),
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert msg == "Discount has expired"

def test_validate_discount_max_uses():
    now = datetime.utcnow()
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        max_uses=10,
        current_uses=10,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert msg == "Discount has reached maximum uses"

def test_validate_discount_min_amount():
    now = datetime.utcnow()
    discount = Discount(
        code="SUMMER2024",
        is_active=True,
        min_order_amount=200.0,
        discount_type="percentage",
        discount_value=20.0,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert msg == "Order amount is below the minimum required for this discount"

def test_calculate_fixed_amount():
    now = datetime.utcnow()
    discount = Discount(
        code="FIXED50",
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=1),
    )
    
    is_valid, amount, msg = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is True
    assert amount == 50.0
