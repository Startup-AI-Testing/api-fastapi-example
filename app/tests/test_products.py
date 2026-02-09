import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base, get_db
from ..main import app
from ..models import Product

# Setup for tests
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
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add some test products
    db.add(Product(name="Laptop", description="A powerful laptop", price=1200.0, stock=5))
    db.add(Product(name="Mouse", description="Wireless mouse", price=25.0, stock=10))
    db.add(Product(name="Monitor", description="4K monitor", price=400.0, stock=0))
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_search_products_by_name():
    with TestClient(app) as client:
        response = client.get("/products/search?q=laptop")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Laptop"

def test_search_products_by_price_range():
    with TestClient(app) as client:
        response = client.get("/products/search?min_price=20&max_price=500")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2 # Mouse and Monitor
        names = [p["name"] for p in data]
        assert "Mouse" in names
        assert "Monitor" in names

def test_search_products_in_stock():
    with TestClient(app) as client:
        response = client.get("/products/search?in_stock=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2 # Laptop and Mouse
        for product in data:
            assert product["stock"] > 0

def test_search_products_combined():
    with TestClient(app) as client:
        response = client.get("/products/search?q=m&min_price=10&in_stock=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Mouse"
