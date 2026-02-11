import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing
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
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_search_products_basic():
    # Create some test products
    client.post("/products/", json={"name": "Laptop", "description": "High-end laptop", "price": 1200.0, "stock": 5})
    client.post("/products/", json={"name": "Mouse", "description": "Wireless mouse", "price": 25.0, "stock": 10})
    client.post("/products/", json={"name": "Keyboard", "description": "Mechanical keyboard", "price": 75.0, "stock": 0})

    # Test search by query
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"

def test_search_products_filters():
    # Create test products
    client.post("/products/", json={"name": "Gaming Laptop", "price": 1500.0, "stock": 3})
    client.post("/products/", json={"name": "Office Laptop", "price": 800.0, "stock": 0})
    client.post("/products/", json={"name": "Mouse", "price": 20.0, "stock": 15})

    # Test price range
    response = client.get("/products/search?min_price=500&max_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Office Laptop"

    # Test in_stock
    response = client.get("/products/search?q=Laptop&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Gaming Laptop"
