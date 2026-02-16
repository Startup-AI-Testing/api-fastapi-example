from app.models import Order

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
    
    assert order.subtotal == 100.0
    assert order.discount_code == "SUMMER2024"
    assert order.discount_amount == 20.0
    assert order.total == 80.0
