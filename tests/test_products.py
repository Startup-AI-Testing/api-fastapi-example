import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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
    # Add some sample data
    p1 = models.Product(name="Laptop Pro", description="High-end laptop", price=1500.0, stock=10)
    p2 = models.Product(name="Laptop Air", description="Thin laptop", price=1000.0, stock=0)
    p3 = models.Product(name="Mouse", description="Wireless mouse", price=50.0, stock=100)
    db.add_all([p1, p2, p3])
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_search_products_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(p["name"] == "Laptop Pro" for p in data)
    assert any(p["name"] == "Laptop Air" for p in data)

def test_search_products_by_price_range():
    response = client.get("/products/search?min_price=1000&max_price=2000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(1000 <= p["price"] <= 2000 for p in data)

def test_search_products_in_stock():
    response = client.get("/products/search?q=laptop&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Pro"

def test_search_products_no_results():
    response = client.get("/products/search?q=smartphone")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
