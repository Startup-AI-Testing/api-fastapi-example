from datetime import datetime, timedelta
from app.schemas import DiscountCreate, OrderCreate, Order

def test_discount_schema_validation():
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.now(),
        "valid_until": datetime.now() + timedelta(days=30),
        "is_active": True
    }
    discount = DiscountCreate(**discount_data)
    assert discount.code == "SUMMER2024"

def test_order_create_schema_with_discount():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**order_data)
    assert order.discount_code == "SUMMER2024"

def test_order_response_schema_with_discount():
    order_data = {
        "id": 1,
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "subtotal": 100.0,
        "discount_code": "SUMMER2024",
        "discount_amount": 20.0,
        "total": 80.0,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "items": []
    }
    order = Order(**order_data)
    assert order.discount_code == "SUMMER2024"
    assert order.subtotal == 100.0
    assert order.discount_amount == 20.0
