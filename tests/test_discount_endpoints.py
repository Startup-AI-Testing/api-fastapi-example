from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_create_discount(client: TestClient):
    discount_data = {
        "code": "TEST20",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=discount_data)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "TEST20"
    assert data["discount_value"] == 20.0

def test_list_active_discounts(client: TestClient):
    # Create an active discount
    client.post("/discounts", json={
        "code": "ACTIVE1",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    # Create an inactive discount
    client.post("/discounts", json={
        "code": "INACTIVE1",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": False
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    codes = [d["code"] for d in data]
    assert "ACTIVE1" in codes
    assert "INACTIVE1" not in codes

def test_validate_discount_endpoint(client: TestClient):
    client.post("/discounts", json={
        "code": "VALIDATE_ME",
        "discount_type": "fixed_amount",
        "discount_value": 15.0,
        "min_order_amount": 50.0,
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    # Valid validation
    response = client.post("/discounts/VALIDATE_ME/validate", params={"subtotal": 100.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["discount_amount"] == 15.0
    
    # Invalid validation (min amount not met)
    response = client.post("/discounts/VALIDATE_ME/validate", params={"subtotal": 30.0})
    assert response.status_code == 400
    assert "Order amount does not meet minimum requirement" in response.json()["detail"]

def test_update_discount_status(client: TestClient):
    client.post("/discounts", json={
        "code": "TOGGLE",
        "discount_type": "percentage",
        "discount_value": 10.0,
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": True
    })
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Check listing
    response = client.get("/discounts")
    codes = [d["code"] for d in response.json()]
    assert "TOGGLE" not in codes
