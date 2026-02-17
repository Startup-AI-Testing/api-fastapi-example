from datetime import datetime, timedelta

def test_create_discount(client):
    valid_from = datetime.utcnow()
    valid_until = valid_from + timedelta(days=30)
    data = {
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "discount_value": 20.0,
        "min_order_amount": 100.0,
        "max_uses": 10,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "is_active": True
    }
    response = client.post("/discounts", json=data)
    assert response.status_code == 201
    assert response.json()["code"] == "SUMMER2024"

def test_get_active_discounts(client, db):
    from app.models import Discount
    d1 = Discount(
        code="D1", discount_type="percentage", discount_value=10.0,
        valid_from=datetime.utcnow(), valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    d2 = Discount(
        code="D2", discount_type="percentage", discount_value=10.0,
        valid_from=datetime.utcnow(), valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=False
    )
    db.add_all([d1, d2])
    db.commit()
    
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "D1"

def test_validate_discount_endpoint(client, db):
    from app.models import Discount
    d1 = Discount(
        code="VALID", discount_type="percentage", discount_value=10.0,
        min_order_amount=50.0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(d1)
    db.commit()
    
    response = client.post("/discounts/VALID/validate?order_amount=100.0")
    assert response.status_code == 200
    assert response.json()["code"] == "VALID"

def test_toggle_discount_status(client, db):
    from app.models import Discount
    d1 = Discount(
        code="TOGGLE", discount_type="percentage", discount_value=10.0,
        valid_from=datetime.utcnow(), valid_until=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    db.add(d1)
    db.commit()
    
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
