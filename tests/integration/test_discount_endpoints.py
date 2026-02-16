import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal

client = TestClient(app)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_discount(db):
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
    assert data["id"] is not None

def test_list_discounts(db):
    # Create a discount first
    client.post(
        "/discounts",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0
        }
    )
    response = client.get("/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "SUMMER2024" for d in data)

def test_validate_discount_endpoint(db):
    client.post(
        "/discounts",
        json={
            "code": "VALIDATE_ME",
            "discount_type": "fixed_amount",
            "discount_value": 50.0,
            "min_order_amount": 100.0
        }
    )
    
    # Valid
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=150.0")
    assert response.status_code == 200
    assert response.json()["valid"] is True
    
    # Invalid amount
    response = client.post("/discounts/VALIDATE_ME/validate?order_amount=50.0")
    assert response.status_code == 400

def test_toggle_discount(db):
    client.post(
        "/discounts",
        json={
            "code": "TOGGLE",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "is_active": True
        }
    )
    
    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False
