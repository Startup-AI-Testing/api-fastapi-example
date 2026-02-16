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
            "max_uses": 50,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_active_discounts(client):
    # Create one active and one inactive
    client.post("/discounts", json={
        "code": "ACTIVE",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    client.post("/discounts", json={
        "code": "INACTIVE",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": False
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    codes = [d["code"] for d in data]
    assert "ACTIVE" in codes
    assert "INACTIVE" not in codes

def test_validate_discount_endpoint(client):
    client.post("/discounts", json={
        "code": "VALIDATE_ME",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "min_order_amount": 50.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    # Valid validation
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=100.0")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 15.0
    
    # Invalid validation (amount too low)
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=30.0")
    assert response.status_code == 400
    assert "Order amount is less than minimum required" in response.json()["detail"]

def test_update_discount_status(client):
    client.post("/discounts", json={
        "code": "TOGGLE",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Verify it's not in active list
    response = client.get("/discounts")
    codes = [d["code"] for d in response.json()]
    assert "TOGGLE" not in codes
