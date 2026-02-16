from datetime import datetime, timedelta
from app.models import Discount, Order

def test_create_discount(db):
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
    db.add(discount)
    db.commit()
    db.refresh(discount)
    
    assert discount.id is not None
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"
    assert discount.discount_value == 20.0

def test_order_with_discount_fields(db):
    order = Order(
        customer_name="John Doe",
        customer_email="john@example.com",
        subtotal=100.0,
        discount_code="SUMMER2024",
        discount_amount=20.0,
        total=80.0
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    assert order.id is not None
    assert order.subtotal == 100.0
    assert order.discount_code == "SUMMER2024"
    assert order.discount_amount == 20.0
    assert order.total == 80.0
