from datetime import datetime, timedelta
from app import models

def test_create_discount(client):
    now = datetime.utcnow()
    discount_data = {
        "code": "NEWYEAR2024",
        "discount_type": "percentage",
        "discount_value": 15.0,
        "min_order_amount": 50.0,
        "max_uses": 100,
        "valid_from": now.isoformat(),
        "valid_until": (now + timedelta(days=30)).isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=discount_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "NEWYEAR2024"
    assert data["discount_value"] == 15.0

def test_list_active_discounts(client, db):
    now = datetime.utcnow()
    d1 = models.Discount(
        code="ACTIVE1", is_active=True, discount_type="percentage", 
        discount_value=10, min_order_amount=0,
        valid_from=now - timedelta(days=1), valid_until=now + timedelta(days=1)
    )
    d2 = models.Discount(
        code="INACTIVE", is_active=False, discount_type="percentage", 
        discount_value=10, min_order_amount=0,
        valid_from=now - timedelta(days=1), valid_until=now + timedelta(days=1)
    )
    d3 = models.Discount(
        code="EXPIRED", is_active=True, discount_type="percentage", 
        discount_value=10, min_order_amount=0,
        valid_from=now - timedelta(days=10), valid_until=now - timedelta(days=1)
    )
    db.add_all([d1, d2, d3])
    db.commit()

    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    # Should only return ACTIVE1
    assert len(data) == 1
    assert data[0]["code"] == "ACTIVE1"

def test_validate_discount_endpoint(client, db):
    now = datetime.utcnow()
    d1 = models.Discount(
        code="VALIDCODE", is_active=True, discount_type="percentage", 
        discount_value=10, min_order_amount=100,
        valid_from=now - timedelta(days=1), valid_until=now + timedelta(days=1)
    )
    db.add(d1)
    db.commit()

    # Valid validation
    response = client.post("/discounts/VALIDCODE/validate", params={"order_amount": 150.0})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["discount_amount"] == 15.0

    # Invalid validation (amount too low)
    response = client.post("/discounts/VALIDCODE/validate", params={"order_amount": 50.0})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["message"] == "Order amount is below the minimum required for this discount"

def test_toggle_discount_status(client, db):
    d1 = models.Discount(
        code="TOGGLE", is_active=True, discount_type="percentage", 
        discount_value=10, min_order_amount=0,
        valid_from=datetime.utcnow(), valid_until=datetime.utcnow() + timedelta(days=1)
    )
    db.add(d1)
    db.commit()

    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    db.refresh(d1)
    assert d1.is_active is False

    # Activate
    response = client.put("/discounts/TOGGLE", json={"is_active": True})
    assert response.status_code == 200
    db.refresh(d1)
    assert d1.is_active is True
