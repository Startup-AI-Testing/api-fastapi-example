import datetime

def test_create_discount(client):
    response = client.post(
        "/discounts/",
        json={
            "code": "TEST20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TEST20"
    assert float(data["discount_value"]) == 20.0

def test_list_discounts(client):
    # Create one
    client.post(
        "/discounts/",
        json={
            "code": "LIST10",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order_amount": 0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    response = client.get("/discounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "LIST10" for d in data)

def test_validate_discount(client):
    # Create one
    client.post(
        "/discounts/",
        json={
            "code": "VALIDATE",
            "discount_type": "fixed_amount",
            "discount_value": 15.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    # Valid
    response = client.post("/discounts/VALIDATE/validate", json={"order_amount": 150.0})
    assert response.status_code == 200
    assert response.json()["is_valid"] is True
    
    # Invalid amount
    response = client.post("/discounts/VALIDATE/validate", json={"order_amount": 50.0})
    assert response.status_code == 200
    assert response.json()["is_valid"] is False
    assert "Minimum order amount" in response.json()["message"]

def test_toggle_discount(client):
    # Create one
    client.post(
        "/discounts/",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order_amount": 0,
            "max_uses": 10,
            "valid_from": datetime.datetime.now().isoformat(),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
            "is_active": True
        }
    )
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Check validation
    response = client.post("/discounts/TOGGLE/validate", json={"order_amount": 100.0})
    assert response.json()["is_valid"] is False
