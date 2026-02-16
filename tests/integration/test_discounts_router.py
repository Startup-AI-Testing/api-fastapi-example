from datetime import datetime, timedelta

def test_create_discount(client):
    response = client.post(
        "/discounts/",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 50,
            "valid_from": (datetime.now() - timedelta(days=1)).isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_discounts(client):
    client.post(
        "/discounts/",
        json={
            "code": "DISC1",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "max_uses": 10,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )
    response = client.get("/discounts/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_validate_discount_endpoint(client):
    client.post(
        "/discounts/",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
        }
    )
    
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=100")
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=30")
    assert response.status_code == 400

def test_toggle_discount(client):
    client.post(
        "/discounts/",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "max_uses": 10,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
