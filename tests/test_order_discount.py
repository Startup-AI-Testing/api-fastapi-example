import pytest
import datetime
from app.models import Product

@pytest.fixture
def test_product(db):
    product = Product(name="Test Product", price=100.0, stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def test_create_order_with_discount(client, test_product):
    # 1. Create a discount
    client.post(
        "/discounts/",
        json={
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    # 2. Create order with discount
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": test_product.id, "quantity": 2}],
            "discount_code": "SAVE20"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    # 2 * 100 = 200 subtotal
    # 20% of 200 = 40 discount
    # 200 - 40 = 160 total
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    assert data["discount_code"] == "SAVE20"
    
    # 3. Verify discount uses increased
    resp = client.get("/discounts/")
    discount = next(d for d in resp.json() if d["code"] == "SAVE20")
    assert discount["current_uses"] == 1

def test_create_order_with_invalid_discount(client, test_product):
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": test_product.id, "quantity": 1}],
            "discount_code": "INVALID"
        }
    )
    assert response.status_code == 400
    assert "Discount code not found" in response.json()["detail"]

def test_create_order_with_insufficient_amount(client, test_product):
    # Create discount with min 500
    client.post(
        "/discounts/",
        json={
            "code": "BIG500",
            "discount_type": "fixed_amount",
            "discount_value": 50.0,
            "min_order_amount": 500.0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": test_product.id, "quantity": 1}], # 100.0 < 500.0
            "discount_code": "BIG500"
        }
    )
    assert response.status_code == 400
    assert "Minimum order amount" in response.json()["detail"]
