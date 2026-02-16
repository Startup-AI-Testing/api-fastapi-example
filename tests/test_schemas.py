from datetime import datetime, timedelta
from app.schemas import DiscountCreate, OrderCreate

def test_discount_schema_validation():
    # Valid discount
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow(),
        "valid_until": datetime.utcnow() + timedelta(days=30),
        "is_active": True
    }
    discount = DiscountCreate(**discount_data)
    assert discount.code == "SUMMER2024"

def test_order_create_with_discount_schema():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": 1, "quantity": 2}
        ],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**order_data)
    assert order.discount_code == "SUMMER2024"
    assert len(order.items) == 1
