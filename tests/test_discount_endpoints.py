from datetime import datetime, timedelta

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
            "max_uses": 100,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["current_uses"] == 0

def test_list_discounts(client):
    response = client.get("/discounts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_validate_discount_endpoint(client):
    # Create a discount first
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = valid_from + timedelta(days=30)
    client.post(
        "/discounts",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    
    # Validate it
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=100.0")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 10.0

def test_toggle_discount_active(client):
    # Create a discount
    client.post(
        "/discounts",
        json={
            "code": "TOGGLE_ME",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "max_uses": 10,
            "valid_from": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    )
    
    # Deactivate it
    response = client.put("/discounts/TOGGLE_ME", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Reactivate it
    response = client.put("/discounts/TOGGLE_ME", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["is_active"] is True
