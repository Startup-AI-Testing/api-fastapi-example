import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Use a separate test database
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

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add some sample products
    products = [
        models.Product(name="Laptop Pro", description="High performance laptop", price=1200.0, stock=10),
        models.Product(name="Laptop Air", description="Thin and light laptop", price=900.0, stock=5),
        models.Product(name="Mouse Wireless", description="Ergonomic mouse", price=25.0, stock=50),
        models.Product(name="Monitor 4K", description="32 inch monitor", price=400.0, stock=0),
    ]
    db.add_all(products)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_search_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("laptop" in item["name"].lower() for item in data)

def test_search_by_price_range():
    response = client.get("/products/search?min_price=300&max_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2 # Laptop Air (900) and Monitor 4K (400)
    assert all(300 <= item["price"] <= 1000 for item in data)

def test_search_in_stock():
    response = client.get("/products/search?q=Monitor&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0 # Monitor 4K has stock 0

def test_search_all_filters():
    response = client.get("/products/search?q=laptop&max_price=1000&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Air"
