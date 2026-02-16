from datetime import datetime, timedelta

def test_create_discount(client):
    valid_until = (datetime.utcnow() + timedelta(days=30)).isoformat()
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_until": valid_until
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["current_uses"] == 0

def test_list_discounts(client):
    # Create a discount first
    client.post(
        "/discounts",
        json={
            "code": "DISCOUNT1",
            "discount_type": "fixed_amount",
            "discount_value": 10.0
        }
    )
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "DISCOUNT1" for d in data)

def test_validate_discount_endpoint(client):
    client.post(
        "/discounts",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_amount": 50.0
        }
    )
    response = client.post("/discounts/VALIDATE_ME/validate", params={"order_amount": 100.0})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 15.0

def test_validate_discount_endpoint_invalid_amount(client):
    client.post(
        "/discounts",
        json={
            "code": "MIN_50",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_amount": 50.0
        }
    )
    response = client.post("/discounts/MIN_50/validate", params={"order_amount": 30.0})
    assert response.status_code == 400
    assert "minimum amount" in response.json()["detail"]

def test_toggle_discount(client):
    client.post(
        "/discounts",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 10.0,
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
