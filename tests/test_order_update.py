from app.models import Order
from app.schemas import OrderCreate

def test_order_model_with_discount_fields(db):
    order = Order(
        customer_name="John Doe",
        customer_email="john@example.com",
        subtotal=100.0,
        discount_amount=20.0,
        total=80.0,
        discount_code="SUMMER2024",
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    assert order.subtotal == 100.0
    assert order.discount_amount == 20.0
    assert order.total == 80.0
    assert order.discount_code == "SUMMER2024"

def test_order_create_schema_with_discount_code():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order_create = OrderCreate(**order_data)
    assert order_create.discount_code == "SUMMER2024"
