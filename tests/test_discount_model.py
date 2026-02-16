from datetime import datetime, timedelta
from app.models import Discount

def test_create_discount():
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=100,
        current_uses=0,
        valid_from=datetime.now(),
        valid_until=datetime.now() + timedelta(days=30),
        is_active=True
    )
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"
    assert discount.discount_value == 20.0
    assert discount.is_active is True
