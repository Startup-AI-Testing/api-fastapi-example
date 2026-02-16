from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError
from app.schemas import DiscountCreate, OrderCreate

def test_discount_create_schema():
    valid_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.now(),
        "valid_until": datetime.now() + timedelta(days=30),
        "is_active": True
    }
    discount = DiscountCreate(**valid_data)
    assert discount.code == "SUMMER2024"
    assert discount.discount_type == "percentage"

def test_discount_create_invalid_type():
    invalid_data = {
        "code": "SUMMER2024",
        "discount_type": "invalid",
        "discount_value": 20.0,
        "valid_from": datetime.now(),
        "valid_until": datetime.now() + timedelta(days=30)
    }
    with pytest.raises(ValidationError):
        DiscountCreate(**invalid_data)

def test_order_create_with_discount_code():
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [{"product_id": 1, "quantity": 2}],
        "discount_code": "SUMMER2024"
    }
    order = OrderCreate(**order_data)
    assert order.discount_code == "SUMMER2024"
