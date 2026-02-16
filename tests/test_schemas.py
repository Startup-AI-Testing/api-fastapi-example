from app.schemas import DiscountCreate, OrderCreate, Order
from datetime import datetime, timedelta

def test_discount_create_schema():
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from,
        "valid_until": valid_until
    }
    schema = DiscountCreate(**data)
    assert schema.code == "SUMMER2024"

def test_order_create_with_discount_schema():
    data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    schema = OrderCreate(**data)
    assert schema.discount_code == "SUMMER2024"

def test_order_response_schema():
    data = {
        "id": 1,
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "subtotal": 100.0,
        "discount_code": "SUMMER2024",
        "discount_amount": 20.0,
        "total": 80.0,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "items": []
    }
    schema = Order(**data)
    assert schema.subtotal == 100.0
    assert schema.discount_amount == 20.0
