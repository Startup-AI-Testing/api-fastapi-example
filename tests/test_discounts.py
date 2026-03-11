from datetime import datetime, timedelta

def test_create_discount(client):
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 100,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=data)
    assert response.status_code == 201
    assert response.json()["code"] == "SUMMER2024"

def test_list_active_discounts(client):
    # Create an active discount
    client.post("/discounts", json={
        "code": "ACTIVE",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    # Create an inactive discount
    client.post("/discounts", json={
        "code": "INACTIVE",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": False
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    discounts = response.json()
    assert len(discounts) == 1
    assert discounts[0]["code"] == "ACTIVE"

def test_validate_discount_endpoint(client):
    client.post("/discounts", json={
        "code": "VALID20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    response = client.post("/discounts/VALID20/validate", json={"order_amount": 150.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["discount_amount"] == 30.0

def test_validate_discount_invalid_amount(client):
    client.post("/discounts", json={
        "code": "MIN100",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    response = client.post("/discounts/MIN100/validate", json={"order_amount": 50.0})
    assert response.status_code == 400
    assert "Order amount is below the minimum required" in response.json()["detail"]

def test_update_discount_status(client):
    client.post("/discounts", json={
        "code": "TOGGLE",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Verify it's not in the active list anymore
    response = client.get("/discounts")
    assert len(response.json()) == 0
