
def test_create_discount(client):
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 100,
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_active_discounts(client):
    # Create an active discount
    client.post("/discounts", json={
        "code": "ACTIVE1", "discount_type": "percentage", "discount_value": 10.0, "is_active": True
    })
    # Create an inactive discount
    client.post("/discounts", json={
        "code": "INACTIVE1", "discount_type": "percentage", "discount_value": 10.0, "is_active": False
    })
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "ACTIVE1"

def test_validate_discount_endpoint(client):
    client.post("/discounts", json={
        "code": "VAL20", "discount_type": "percentage", "discount_value": 20.0, "min_order_amount": 100.0
    })
    
    # Valid
    response = client.post("/discounts/VAL20/validate", params={"order_amount": 150.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    # Invalid amount
    response = client.post("/discounts/VAL20/validate", params={"order_amount": 50.0})
    assert response.status_code == 400
    assert "Order amount is below the minimum" in response.json()["detail"]

def test_toggle_discount_status(client):
    client.post("/discounts", json={
        "code": "TOGGLE", "discount_type": "percentage", "discount_value": 10.0, "is_active": True
    })
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Check listing
    response = client.get("/discounts")
    assert len(response.json()) == 0
