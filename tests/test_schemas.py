from app.schemas import DiscountCreate, OrderCreate, Order
from datetime import datetime, timedelta

def test_discount_create_schema():
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "is_active": True
    }
    discount_in = DiscountCreate(**data)
    assert discount_in.code == "SUMMER2024"

def test_order_create_with_discount_code():
    data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order_in = OrderCreate(**data)
    assert order_in.discount_code == "SUMMER2024"

def test_order_schema_with_discount_fields():
    data = {
        "id": 1,
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [],
        "subtotal": 100.0,
        "discount_amount": 20.0,
        "discount_code": "SUMMER2024",
        "total": 80.0,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    order = Order(**data)
    assert order.subtotal == 100.0
    assert order.discount_amount == 20.0
    assert order.discount_code == "SUMMER2024"
    assert order.total == 80.0
