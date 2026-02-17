from datetime import datetime, timedelta
from app import models


def test_create_discount(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0


def test_get_active_discounts(client, db):
    # Create one active and one inactive discount
    d1 = models.Discount(
        code="ACTIVE1",
        discount_type="percentage",
        discount_value=10.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True,
    )
    d2 = models.Discount(
        code="INACTIVE1",
        discount_type="percentage",
        discount_value=10.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=False,
    )
    db.add_all([d1, d2])
    db.commit()

    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "ACTIVE1"


def test_validate_discount_endpoint(client, db):
    d1 = models.Discount(
        code="VALIDCODE",
        discount_type="percentage",
        discount_value=10.0,
        min_order_amount=50.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True,
    )
    db.add(d1)
    db.commit()

    # Valid validation
    response = client.post(
        "/discounts/VALIDCODE/validate", params={"order_amount": 100.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["discount_amount"] == 10.0

    # Invalid validation (min amount)
    response = client.post(
        "/discounts/VALIDCODE/validate", params={"order_amount": 30.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert "less than the minimum" in data["error"]


def test_update_discount_status(client, db):
    d1 = models.Discount(
        code="TOGGLE",
        discount_type="percentage",
        discount_value=10.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True,
    )
    db.add(d1)
    db.commit()

    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    db.refresh(d1)
    assert d1.is_active is False
