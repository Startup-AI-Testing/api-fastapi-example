from app.schemas import DiscountCreate, OrderCreate
from datetime import datetime, timedelta

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

def test_order_create_with_discount_code():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**order_data)
    assert order.discount_code == "SUMMER2024"
