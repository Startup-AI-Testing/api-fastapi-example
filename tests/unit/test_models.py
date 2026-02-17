from app.models import Discount, Order
from datetime import datetime, timedelta

def test_create_discount():
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True
    )
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"
    assert discount.discount_value == 20.0
    assert discount.is_active is True

def test_order_with_discount_fields():
    order = Order(
        customer_name="John Doe",
        customer_email="john@example.com",
        subtotal=100.0,
        discount_code="SUMMER2024",
        discount_amount=20.0,
        total=80.0
    )
    assert order.subtotal == 100.0
    assert order.discount_code == "SUMMER2024"
    assert order.discount_amount == 20.0
    assert order.total == 80.0
