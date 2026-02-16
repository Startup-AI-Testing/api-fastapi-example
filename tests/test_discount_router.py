import pytest
from datetime import datetime, timedelta

def test_create_discount(client):
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["current_uses"] == 0

def test_list_discounts(client):
    # Create one first
    client.post(
        "/discounts",
        json={
            "code": "PROMO1",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "PROMO1" for d in data)

def test_validate_discount_endpoint(client):
    client.post(
        "/discounts",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_amount": 50.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )
    
    # Valid
    response = client.post("/discounts/VALIDATE_ME/validate", params={"order_amount": 100.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["discount_amount"] == 15.0

    # Below min amount
    response = client.post("/discounts/VALIDATE_ME/validate", params={"order_amount": 30.0})
    assert response.status_code == 400
    assert "below the minimum required" in response.json()["detail"]

def test_toggle_discount(client):
    client.post(
        "/discounts",
        json={
            "code": "TOGGLE",
            "discount_type": "fixed_amount",
            "discount_value": 5.0,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Validate should now fail
    response = client.post("/discounts/TOGGLE/validate", params={"order_amount": 100.0})
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]
