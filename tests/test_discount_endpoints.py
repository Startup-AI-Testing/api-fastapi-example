from datetime import datetime, timedelta

def test_create_discount(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    response = client.post(
        "/discounts/",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat()
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"

def test_list_active_discounts(client):
    # First create one
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    client.post(
        "/discounts/",
        json={
            "code": "ACTIVE1",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order_amount": 0.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    # Create an inactive one
    client.post(
        "/discounts/",
        json={
            "code": "INACTIVE1",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order_amount": 0.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": False
        }
    )
    
    response = client.get("/discounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    codes = [d["code"] for d in data]
    assert "ACTIVE1" in codes
    assert "INACTIVE1" not in codes

def test_validate_discount_endpoint(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    client.post(
        "/discounts/",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat()
        }
    )
    
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=150.0")
    assert response.status_code == 200
    assert response.json()["code"] == "VALIDATE_ME"

def test_update_discount_status(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=7)
    client.post(
        "/discounts/",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
