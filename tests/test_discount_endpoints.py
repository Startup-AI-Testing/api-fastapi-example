from datetime import datetime, timedelta

def test_create_discount_endpoint(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    discount_data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    response = client.post("/discounts/", json=discount_data)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_discounts_endpoint(client):
    # Create a discount first
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    discount_data = {
        "code": "LIST_TEST",
        "discount_type": "fixed_amount",
        "discount_value": 10.0,
        "min_order_amount": 50.0,
        "max_uses": 5,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    client.post("/discounts/", json=discount_data)
    
    response = client.get("/discounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "LIST_TEST" for d in data)

def test_validate_discount_endpoint(client):
    # Create a discount first
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    discount_data = {
        "code": "VALIDATE_ME",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    client.post("/discounts/", json=discount_data)
    
    # Validate it
    response = client.post("/discounts/VALIDATE_ME/validate", json={"order_amount": 150.0})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 22.5

def test_update_discount_endpoint(client):
    # Create a discount first
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    discount_data = {
        "code": "UPDATE_ME",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "min_order_amount": 50.0,
        "max_uses": 5,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    client.post("/discounts/", json=discount_data)
    
    # Update it
    response = client.put("/discounts/UPDATE_ME", json={"is_active": False, "discount_value": 15.0})
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    assert data["discount_value"] == 15.0
