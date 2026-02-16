import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app.models import Discount

def test_calculate_percentage_discount():
    discount = Discount(
        code="SUMMER20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    
    # Order amount 200, 20% of 200 is 40
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 40.0
    
    # Order amount 50, less than min_order_amount
    # The service should probably handle this validation separately, 
    # but let's see how we implement it.
    # If we only call calculate_discount after validation, it's fine.

def test_calculate_fixed_amount_discount():
    discount = Discount(
        code="FIXED50",
        discount_type="fixed_amount",
        discount_value=50.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=0
    )
    
    amount = DiscountService.calculate_discount(discount, 200.0)
    assert amount == 50.0
    
    # Discount value more than order amount
    amount = DiscountService.calculate_discount(discount, 30.0)
    assert amount == 30.0 # Should not exceed order amount

def test_validate_discount_success():
    discount = Discount(
        code="VALID",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=100.0,
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=10,
        current_uses=5
    )
    
    # Should not raise exception
    DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_inactive():
    discount = Discount(code="INACTIVE", is_active=False)
    with pytest.raises(ValueError, match="Discount is not active"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_expired():
    discount = Discount(
        code="EXPIRED",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(days=1)
    )
    with pytest.raises(ValueError, match="Discount has expired"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_not_started():
    discount = Discount(
        code="FUTURE",
        is_active=True,
        valid_from=datetime.utcnow() + timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=2)
    )
    with pytest.raises(ValueError, match="Discount is not yet valid"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_max_uses():
    discount = Discount(
        code="MAXED",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        max_uses=5,
        current_uses=5
    )
    with pytest.raises(ValueError, match="Discount has reached maximum uses"):
        DiscountService.validate_discount(discount, 150.0)

def test_validate_discount_min_amount():
    discount = Discount(
        code="MIN_AMT",
        is_active=True,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        min_order_amount=200.0
    )
    with pytest.raises(ValueError, match="Order amount is below the minimum required"):
        DiscountService.validate_discount(discount, 150.0)
