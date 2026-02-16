import pytest
from datetime import datetime, timedelta
from app import models

def test_create_discount(client):
    payload = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 50,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_active_discounts(client, db):
    d1 = models.Discount(code="D1", discount_type="percentage", discount_value=10, is_active=True)
    d2 = models.Discount(code="D2", discount_type="fixed_amount", discount_value=5, is_active=False)
    db.add_all([d1, d2])
    db.commit()

    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "D1"

def test_validate_discount_endpoint(client, db):
    d1 = models.Discount(
        code="VALID_CODE",
        discount_type="percentage",
        discount_value=10,
        min_order_amount=50,
        is_active=True
    )
    db.add(d1)
    db.commit()

    # Valid
    response = client.post("/discounts/VALID_CODE/validate", json={"order_amount": 100.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True

    # Invalid (amount too low)
    response = client.post("/discounts/VALID_CODE/validate", json={"order_amount": 30.0})
    assert response.status_code == 400
    assert "below the minimum" in response.json()["detail"]

def test_toggle_discount_status(client, db):
    d1 = models.Discount(code="TOGGLE", discount_type="percentage", discount_value=10, is_active=True)
    db.add(d1)
    db.commit()

    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    db.refresh(d1)
    assert d1.is_active is False
