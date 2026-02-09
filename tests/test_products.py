import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Product

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

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Add some test products
    p1 = Product(name="Laptop", description="High performance laptop", price=1200.0, stock=10)
    p2 = Product(name="Mouse", description="Wireless mouse", price=25.0, stock=50)
    p3 = Product(name="Keyboard", description="Mechanical keyboard", price=80.0, stock=0)
    p4 = Product(name="Monitor", description="4K Monitor", price=400.0, stock=5)
    db.add_all([p1, p2, p3, p4])
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_search_products_by_name(client):
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"

def test_search_products_by_price_range(client):
    response = client.get("/products/search?min_price=50&max_price=500")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Keyboard" in names
    assert "Monitor" in names

def test_search_products_in_stock(client):
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for p in data:
        assert p["stock"] > 0

def test_search_products_no_results(client):
    response = client.get("/products/search?q=nonexistent")
    assert response.status_code == 200
    assert response.json() == []
