import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_discount(client):
    response = client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0

def test_list_discounts(client):
    client.post("/discounts", json={"code": "D1", "discount_type": "percentage", "discount_value": 10})
    client.post("/discounts", json={"code": "D2", "discount_type": "fixed_amount", "discount_value": 5})
    
    response = client.get("/discounts")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_validate_discount_endpoint(client):
    client.post(
        "/discounts",
        json={
            "code": "VALID",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "min_order_amount": 50.0,
            "is_active": True
        }
    )
    
    response = client.post("/discounts/VALID/validate?order_amount=100.0")
    assert response.status_code == 200
    assert response.json()["code"] == "VALID"
    
    response = client.post("/discounts/VALID/validate?order_amount=30.0")
    assert response.status_code == 400

def test_toggle_discount(client):
    client.post("/discounts", json={"code": "TOGGLE", "discount_type": "percentage", "discount_value": 10})
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    
    # Activate
    response = client.put("/discounts/TOGGLE", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["is_active"] is True
