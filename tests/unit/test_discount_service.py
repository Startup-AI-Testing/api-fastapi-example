import pytest
from datetime import datetime, timedelta
from app.services.discount_service import DiscountService
from app import models

def test_validate_discount_success(db):
    discount = models.Discount(
        code="TEST10",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    # Should not raise exception
    DiscountService.validate_discount(db, "TEST10", 100.0)

def test_validate_discount_not_found(db):
    with pytest.raises(Exception) as excinfo:
        DiscountService.validate_discount(db, "NONEXISTENT", 100.0)
    assert "Invalid discount code" in str(excinfo.value)

def test_validate_discount_inactive(db):
    discount = models.Discount(
        code="INACTIVE",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=False
    )
    db.add(discount)
    db.commit()

    with pytest.raises(Exception) as excinfo:
        DiscountService.validate_discount(db, "INACTIVE", 100.0)
    assert "Discount is not active" in str(excinfo.value)

def test_validate_discount_expired(db):
    discount = models.Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=2),
        valid_until=datetime.now() - timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(Exception) as excinfo:
        DiscountService.validate_discount(db, "EXPIRED", 100.0)
    assert "Discount has expired" in str(excinfo.value)

def test_validate_discount_no_uses_left(db):
    discount = models.Discount(
        code="NOUSES",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=5,
        current_uses=5,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(Exception) as excinfo:
        DiscountService.validate_discount(db, "NOUSES", 100.0)
    assert "Discount usage limit reached" in str(excinfo.value)

def test_validate_discount_min_amount(db):
    discount = models.Discount(
        code="MIN50",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=50.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    with pytest.raises(Exception) as excinfo:
        DiscountService.validate_discount(db, "MIN50", 30.0)
    assert "Order amount is less than minimum required" in str(excinfo.value)

def test_apply_discount_percentage(db):
    discount = models.Discount(
        code="PERC10",
        discount_type="percentage",
        discount_value=10.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    amount = DiscountService.apply_discount(db, "PERC10", 100.0)
    assert amount == 10.0
    
    db.refresh(discount)
    assert discount.current_uses == 1

def test_apply_discount_fixed(db):
    discount = models.Discount(
        code="FIXED20",
        discount_type="fixed_amount",
        discount_value=20.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.now() - timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=1),
        is_active=True
    )
    db.add(discount)
    db.commit()

    amount = DiscountService.apply_discount(db, "FIXED20", 100.0)
    assert amount == 20.0
    
    db.refresh(discount)
    assert discount.current_uses == 1
