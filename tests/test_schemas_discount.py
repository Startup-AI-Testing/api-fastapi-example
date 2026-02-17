from datetime import datetime, timedelta
from app.schemas import DiscountCreate, Discount, OrderCreate, Order

def test_discount_create_schema():
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
    discount = DiscountCreate(**discount_data)
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"

def test_order_create_schema_with_discount():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**order_data)
    assert order.discount_code == "SUMMER2024"

def test_order_schema_with_discount_fields():
    order_data = {
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
    order = Order(**order_data)
    assert order.subtotal == 100.0
    assert order.discount_amount == 20.0
    assert order.total == 80.0
