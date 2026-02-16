from datetime import datetime, timedelta
from app.schemas import DiscountCreate, OrderCreate

def test_discount_create_schema():
    valid_until = datetime.utcnow() + timedelta(days=30)
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_until": valid_until
    }
    discount = DiscountCreate(**data)
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"

def test_order_create_with_discount_schema():
    data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**data)
    assert order.discount_code == "SUMMER2024"
    assert len(order.items) == 1
