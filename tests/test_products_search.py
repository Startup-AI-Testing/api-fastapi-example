import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Setup test database
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
    # Add some sample products
    products = [
        models.Product(name="Laptop Pro", description="High performance laptop", price=1200.0, stock=5),
        models.Product(name="Laptop Air", description="Thin and light laptop", price=900.0, stock=0),
        models.Product(name="Smartphone", description="Latest smartphone", price=600.0, stock=10),
        models.Product(name="Mouse", description="Wireless mouse", price=25.0, stock=50),
    ]
    db.add_all(products)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_search_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("laptop" in item["name"].lower() for item in data)

def test_search_by_price_range():
    response = client.get("/products/search?min_price=100&max_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # Laptop Air (900) and Smartphone (600)
    assert all(100 <= item["price"] <= 1000 for item in data)

def test_search_in_stock():
    response = client.get("/products/search?q=laptop&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Pro"
    assert data[0]["stock"] > 0

def test_search_no_results():
    response = client.get("/products/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
