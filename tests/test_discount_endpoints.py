from datetime import datetime, timedelta

def test_create_discount(client):
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=discount_data)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["current_uses"] == 0

def test_get_discounts(client):
    # Create a discount first
    client.post("/discounts", json={
        "code": "PROMO10",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "PROMO10" for d in data)

def test_validate_discount_endpoint(client):
    # Create a discount
    client.post("/discounts", json={
        "code": "VALIDATE_ME",
        "discount_type": "fixed_amount",
        "discount_value": 50.0,
        "min_order_amount": 100.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    # Valid validation
    response = client.post("/discounts/VALIDATE_ME/validate", params={"order_amount": 150.0})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 50.0
    
    # Invalid validation (amount too low)
    response = client.post("/discounts/VALIDATE_ME/validate", params={"order_amount": 50.0})
    assert response.status_code == 400
    assert "below the minimum" in response.json()["detail"]

def test_update_discount_status(client):
    # Create a discount
    client.post("/discounts", json={
        "code": "TOGGLE_ME",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    # Deactivate
    response = client.put("/discounts/TOGGLE_ME", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Try to validate deactivated discount
    response = client.post("/discounts/TOGGLE_ME/validate", params={"order_amount": 100.0})
    assert response.status_code == 400
    assert "not active" in response.json()["detail"]
