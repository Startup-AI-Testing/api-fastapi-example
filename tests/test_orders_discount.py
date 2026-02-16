import pytest
from datetime import datetime, timedelta


@pytest.fixture
def product(client):
    response = client.post(
        "/products/", json={"name": "Test Product", "price": 100.0, "stock": 10}
    )
    return response.json()


@pytest.fixture
def discount_percentage(client):
    response = client.post(
        "/discounts/",
        json={
            "code": "PERCENT20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )
    return response.json()


@pytest.fixture
def discount_fixed(client):
    response = client.post(
        "/discounts/",
        json={
            "code": "FIXED10",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "min_order_amount": 50.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )
    return response.json()


def test_create_order_with_percentage_discount(client, product, discount_percentage):
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product["id"], "quantity": 2}],
            "discount_code": "PERCENT20",
        },
    )
    assert response.status_code == 201
    data = response.json()
    # 2 * 100 = 200 subtotal
    # 20% of 200 = 40 discount
    # 200 - 40 = 160 total
    assert data["subtotal"] == 200.0
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    assert data["discount_code"] == "PERCENT20"


def test_create_order_with_fixed_discount(client, product, discount_fixed):
    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product["id"], "quantity": 1}],
            "discount_code": "FIXED10",
        },
    )
    assert response.status_code == 201
    data = response.json()
    # 1 * 100 = 100 subtotal
    # 10 fixed discount
    # 100 - 10 = 90 total
    assert data["subtotal"] == 100.0
    assert data["discount_amount"] == 10.0
    assert data["total"] == 90.0


def test_order_min_amount_not_met(client, product):
    # Create discount with high min amount
    client.post(
        "/discounts/",
        json={
            "code": "HIGHMIN",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "min_order_amount": 500.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product["id"], "quantity": 1}],
            "discount_code": "HIGHMIN",
        },
    )
    assert response.status_code == 400
    assert "Minimum order amount" in response.json()["detail"]


def test_discount_max_uses_reached(client, product):
    # Create discount with 1 max use
    client.post(
        "/discounts/",
        json={
            "code": "ONETIME",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "max_uses": 1,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )

    # Use it once
    response = client.post(
        "/orders/",
        json={
            "customer_name": "User 1",
            "customer_email": "user1@example.com",
            "items": [{"product_id": product["id"], "quantity": 1}],
            "discount_code": "ONETIME",
        },
    )
    assert response.status_code == 201

    # Use it again
    response = client.post(
        "/orders/",
        json={
            "customer_name": "User 2",
            "customer_email": "user2@example.com",
            "items": [{"product_id": product["id"], "quantity": 1}],
            "discount_code": "ONETIME",
        },
    )
    assert response.status_code == 400
    assert "maximum uses" in response.json()["detail"]


def test_discount_expired(client, product):
    # Create expired discount
    client.post(
        "/discounts/",
        json={
            "code": "EXPIRED",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "valid_from": (datetime.now() - timedelta(days=10)).isoformat(),
            "valid_until": (datetime.now() - timedelta(days=1)).isoformat(),
            "is_active": True,
        },
    )

    response = client.post(
        "/orders/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": product["id"], "quantity": 1}],
            "discount_code": "EXPIRED",
        },
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"]
