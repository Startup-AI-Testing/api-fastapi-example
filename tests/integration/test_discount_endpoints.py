from datetime import datetime, timedelta

def test_create_discount(client):
    payload = {
        "code": "WINTER2024",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "min_order_amount": 50.0,
        "max_uses": 100,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "WINTER2024"
    assert data["id"] is not None

def test_list_active_discounts(client):
    # Create an active discount
    client.post("/discounts", json={
        "code": "ACTIVE1",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 0.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    # Create an inactive discount
    client.post("/discounts", json={
        "code": "INACTIVE1",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 0.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": False
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    codes = [d["code"] for d in data]
    assert "ACTIVE1" in codes
    assert "INACTIVE1" not in codes

def test_validate_discount_endpoint(client):
    client.post("/discounts", json={
        "code": "VALIDATE_ME",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    # Valid
    response = client.post("/discounts/VALIDATE_ME/validate", json={"order_amount": 150.0})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True, f"Validation failed: {data.get('error')}"
    
    # Invalid (amount)
    response = client.post("/discounts/VALIDATE_ME/validate", json={"order_amount": 50.0})
    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert "below the minimum" in response.json()["error"]

def test_toggle_discount_status(client):
    client.post("/discounts", json={
        "code": "TOGGLE_ME",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 0.0,
        "max_uses": 10,
        "valid_from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "is_active": True
    })
    
    # Deactivate
    response = client.put("/discounts/TOGGLE_ME", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Verify it's not in active list
    response = client.get("/discounts")
    codes = [d["code"] for d in response.json()]
    assert "TOGGLE_ME" not in codes
