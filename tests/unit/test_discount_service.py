from datetime import datetime, timedelta
from app import models
from app.services.discount_service import DiscountService


def test_validate_discount_success(db):
    discount = models.Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    # Valid order amount
    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is True
    assert error is None


def test_validate_discount_inactive(db):
    discount = models.Discount(
        code="INACTIVE",
        discount_type="percentage",
        discount_value=20.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=False,
    )
    db.add(discount)
    db.commit()

    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount is not active"


def test_validate_discount_expired(db):
    discount = models.Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount has expired or is not yet valid"


def test_validate_discount_max_uses(db):
    discount = models.Discount(
        code="MAX_USES",
        discount_type="percentage",
        discount_value=20.0,
        max_uses=5,
        current_uses=5,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Discount has reached its maximum uses"


def test_validate_discount_min_amount(db):
    discount = models.Discount(
        code="MIN_AMOUNT",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=200.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    is_valid, error = DiscountService.validate_discount(discount, 150.0)
    assert is_valid is False
    assert error == "Order amount is less than the minimum required for this discount"


def test_calculate_discount_percentage():
    discount = models.Discount(discount_type="percentage", discount_value=20.0)
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 20.0


def test_calculate_discount_fixed():
    discount = models.Discount(discount_type="fixed_amount", discount_value=15.0)
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 15.0


def test_calculate_discount_fixed_more_than_total():
    discount = models.Discount(discount_type="fixed_amount", discount_value=150.0)
    amount = DiscountService.calculate_discount_amount(discount, 100.0)
    assert amount == 100.0
