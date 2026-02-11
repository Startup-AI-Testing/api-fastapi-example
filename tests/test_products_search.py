from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.database import Base, get_db
from app.models import Product

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    # Add sample data
    p1 = Product(name="Laptop Pro", description="High performance laptop", price=1200.0, stock=10)
    p2 = Product(name="Smartphone", description="Latest model", price=800.0, stock=5)
    p3 = Product(name="USB-C Cable", description="2 meters cable", price=15.0, stock=0)
    p4 = Product(name="Gaming Mouse", description="RGB gaming mouse", price=50.0, stock=20)
    
    db.add_all([p1, p2, p3, p4])
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def test_search_by_name(client):
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Pro"

def test_search_by_price_range(client):
    response = client.get("/products/search?min_price=10&max_price=100")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "USB-C Cable" in names
    assert "Gaming Mouse" in names

def test_search_in_stock(client):
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for p in data:
        assert p["stock"] > 0

def test_search_combined(client):
    response = client.get("/products/search?q=phone&max_price=900&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Smartphone"

def test_search_no_results(client):
    response = client.get("/products/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
