from datetime import datetime, timedelta
from app import models


def test_create_order_with_discount_success(client, db):
    # Create a product
    product = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(product)

    # Create a discount
    discount = models.Discount(
        code="SAVE20",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        max_uses=10,
        current_uses=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "SAVE20",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 1000.0
    assert data["discount_code"] == "SAVE20"
    assert data["discount_amount"] == 200.0
    assert data["total"] == 800.0

    # Verify discount uses increased
    db.refresh(discount)
    assert discount.current_uses == 1


def test_create_order_with_invalid_discount(client, db):
    product = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(product)
    db.commit()

    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "INVALID",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Discount code not found"


def test_create_order_with_expired_discount(client, db):
    product = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(product)

    discount = models.Discount(
        code="EXPIRED",
        discount_type="percentage",
        discount_value=20.0,
        valid_from=datetime.utcnow() - timedelta(days=10),
        valid_until=datetime.utcnow() - timedelta(days=1),
        is_active=True,
    )
    db.add(discount)
    db.commit()

    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
            "discount_code": "EXPIRED",
        },
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()


def test_create_order_without_discount(client, db):
    product = models.Product(name="Laptop", price=1000.0, stock=5)
    db.add(product)
    db.commit()

    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product.id, "quantity": 1}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 1000.0
    assert data["discount_code"] is None
    assert data["discount_amount"] == 0.0
    assert data["total"] == 1000.0
