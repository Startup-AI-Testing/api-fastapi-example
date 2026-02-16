import pytest
from datetime import datetime, timedelta

def test_create_discount(client, db):
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 100,
            "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_active_discounts(client, db):
    # Create an active discount
    client.post(
        "/discounts",
        json={
            "code": "ACTIVE",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
    )
    # Create an inactive discount
    client.post(
        "/discounts",
        json={
            "code": "INACTIVE",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "is_active": False
        }
    )
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "ACTIVE"

def test_validate_discount_code(client, db):
    client.post(
        "/discounts",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_amount": 50.0,
            "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
    )
    
    response = client.post("/discounts/VALIDATE_ME/validate", json={"order_amount": 100.0})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 15.0

def test_toggle_discount(client, db):
    client.post(
        "/discounts",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
    )
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Reactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["is_active"] is True
