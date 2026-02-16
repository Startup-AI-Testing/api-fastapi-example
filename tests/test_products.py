import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models

# Setup test database
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
    db = TestingSessionLocal()
    # Seed data
    db.add(
        models.Product(
            name="Laptop Pro",
            description="High performance laptop",
            price=1200.0,
            stock=10,
        )
    )
    db.add(
        models.Product(
            name="Laptop Air", description="Lightweight laptop", price=900.0, stock=5
        )
    )
    db.add(
        models.Product(
            name="Smartphone", description="Latest smartphone", price=800.0, stock=0
        )
    )
    db.add(
        models.Product(name="Mouse", description="Wireless mouse", price=25.0, stock=50)
    )
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


def test_search_products_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("laptop" in item["name"].lower() for item in data)


def test_search_products_by_price_range():
    response = client.get("/products/search?min_price=100&max_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Laptop Air (900) and Smartphone (800)
    assert all(100 <= item["price"] <= 1000 for item in data)


def test_search_products_in_stock():
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Laptop Pro, Laptop Air, Mouse
    assert all(item["stock"] > 0 for item in data)


def test_search_products_combined():
    response = client.get("/products/search?q=laptop&min_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Pro"
