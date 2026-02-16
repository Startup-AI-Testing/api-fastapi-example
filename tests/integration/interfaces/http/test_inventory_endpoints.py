import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Product, Inventory
from datetime import datetime

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add test product
    product = Product(id=1, name="Test Product", price=10.0)
    db.add(product)
    # Add initial inventory
    inventory = Inventory(
        product_id=1,
        quantity_available=100,
        quantity_reserved=0,
        quantity_sold=0,
        reorder_point=10,
        version=1,
        last_restocked_at=datetime.utcnow()
    )
    db.add(inventory)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_reserve_stock():
    response = client.post("/inventory/reserve", json={"product_id": 1, "quantity": 5, "reservation_type": "order"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["quantity"] == 5

def test_confirm_reservation():
    # First reserve
    res_response = client.post("/inventory/reserve", json={"product_id": 1, "quantity": 5, "reservation_type": "order"})
    res_id = res_response.json()["id"]
    
    # Then confirm
    response = client.post(f"/inventory/reserve/{res_id}/confirm", json={"order_id": "order-123"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

def test_release_reservation():
    # First reserve
    res_response = client.post("/inventory/reserve", json={"product_id": 1, "quantity": 5, "reservation_type": "order"})
    res_id = res_response.json()["id"]
    
    # Then release
    response = client.delete(f"/inventory/reserve/{res_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "released"

def test_get_availability():
    response = client.get("/inventory/product/1")
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 100

def test_restock():
    response = client.post("/inventory/restock", json={"product_id": 1, "quantity": 50, "created_by": "admin"})
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 150

def test_adjust_stock():
    response = client.post("/inventory/adjust", json={"product_id": 1, "quantity": -10, "reason": "damaged", "created_by": "admin"})
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 90

def test_get_movements():
    # Make some movement
    client.post("/inventory/restock", json={"product_id": 1, "quantity": 50, "created_by": "admin"})
    
    response = client.get("/inventory/movements")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_low_stock():
    # Set low stock
    db = TestingSessionLocal()
    inv = db.query(Inventory).filter_by(product_id=1).first()
    inv.quantity_available = 5
    db.commit()
    
    response = client.get("/inventory/low-stock")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_id"] == 1
