from app.models import Discount

def test_create_discount(client):
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "is_active": True
    }
    response = client.post("/discounts", json=data)
    assert response.status_code == 201
    assert response.json()["code"] == "SUMMER2024"

def test_list_active_discounts(client, db):
    discount1 = Discount(code="D1", discount_type="percentage", discount_value=10, is_active=True)
    discount2 = Discount(code="D2", discount_type="percentage", discount_value=20, is_active=False)
    db.add(discount1)
    db.add(discount2)
    db.commit()
    
    response = client.get("/discounts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "D1"

def test_validate_discount_endpoint(client, db):
    discount = Discount(
        code="SUMMER2024",
        discount_type="percentage",
        discount_value=20.0,
        min_order_amount=100.0,
        is_active=True
    )
    db.add(discount)
    db.commit()
    
    # Valid
    response = client.post("/discounts/SUMMER2024/validate", json={"order_amount": 150.0})
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    # Invalid (amount)
    response = client.post("/discounts/SUMMER2024/validate", json={"order_amount": 50.0})
    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert "below minimum" in response.json()["error"]

def test_update_discount_status(client, db):
    discount = Discount(code="D1", discount_type="percentage", discount_value=10, is_active=True)
    db.add(discount)
    db.commit()
    
    response = client.put("/discounts/D1", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    db.refresh(discount)
    assert discount.is_active is False
