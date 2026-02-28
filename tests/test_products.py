import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Add some test products
    p1 = models.Product(name="Laptop", description="A powerful laptop", price=1000.0, stock=10)
    p2 = models.Product(name="Mouse", description="Wireless mouse", price=25.0, stock=50)
    p3 = models.Product(name="Keyboard", description="Mechanical keyboard", price=75.0, stock=0)
    p4 = models.Product(name="Monitor", description="4K monitor", price=400.0, stock=5)
    
    db.add_all([p1, p2, p3, p4])
    db.commit()
    
    yield
    
    Base.metadata.drop_all(bind=engine)


def test_search_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"


def test_search_by_name_case_insensitive():
    response = client.get("/products/search?q=LAPTOP")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"


def test_search_by_price_range():
    response = client.get("/products/search?min_price=50&max_price=500")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Keyboard (75) and Monitor (400)
    names = [p["name"] for p in data]
    assert "Keyboard" in names
    assert "Monitor" in names


def test_search_in_stock():
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Laptop, Mouse, Monitor (Keyboard has 0 stock)
    names = [p["name"] for p in data]
    assert "Keyboard" not in names


def test_search_combined_filters():
    response = client.get("/products/search?q=o&min_price=10&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    # Laptop (1000, 10), Mouse (25, 50), Monitor (400, 5) all have 'o' in name
    # Keyboard (75, 0) has 'o' but is out of stock
    assert len(data) == 3
    names = [p["name"] for p in data]
    assert "Laptop" in names
    assert "Mouse" in names
    assert "Monitor" in names
    assert "Keyboard" not in names


def test_search_no_results():
    response = client.get("/products/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
