import pytest
from datetime import datetime, timedelta
from app.models import Discount
from app.services.discount_service import DiscountService
from app.errors import DiscountError

def test_validate_valid_discount(db):
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    validated_discount = DiscountService.validate_discount(db, "SUMMER2024", 150.0)
    assert validated_discount.code == "SUMMER2024"

def test_validate_expired_discount(db):
    discount = Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(DiscountError, match="Discount code has expired"):
        DiscountService.validate_discount(db, "EXPIRED", 150.0)

def test_validate_max_uses_reached(db):
    discount = Discount(
        code="FULL",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=10,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(DiscountError, match="Discount code has reached maximum uses"):
        DiscountService.validate_discount(db, "FULL", 150.0)

def test_validate_min_amount_not_reached(db):
    discount = Discount(
        code="MIN100",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(DiscountError, match="Order amount is below the minimum required"):
        DiscountService.validate_discount(db, "MIN100", 50.0)

def test_calculate_discount_percentage():
    discount = Discount(discount_type="percentage", discount_value=20.0)
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 20.0

def test_calculate_discount_fixed():
    discount = Discount(discount_type="fixed_amount", discount_value=15.0)
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 15.0
