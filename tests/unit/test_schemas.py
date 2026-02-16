from app.schemas import DiscountCreate, Discount
from datetime import datetime, timedelta

def test_discount_schema():
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "is_active": True
    }
    discount_create = DiscountCreate(**discount_data)
    assert discount_create.code == "SUMMER2024"
    
    discount_out = Discount(
        id=1,
        current_uses=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        **discount_data
    )
    assert discount_out.id == 1
    assert discount_out.current_uses == 0

def test_order_schema_with_discount():
    from app.schemas import OrderCreate, Order
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order_create = OrderCreate(**order_data)
    assert order_create.discount_code == "SUMMER2024"

    order_out = Order(
        id=1,
        total=80.0,
        subtotal=100.0,
        discount_amount=20.0,
        discount_code="SUMMER2024",
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        customer_name="John Doe",
        customer_email="john@example.com",
        items=[]
    )
    assert order_out.subtotal == 100.0
    assert order_out.discount_amount == 20.0
    assert order_out.discount_code == "SUMMER2024"
