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
    # Add some sample data
    db.add(
        models.Product(
            name="Laptop", description="High-end laptop", price=1200.0, stock=10
        )
    )
    db.add(
        models.Product(name="Mouse", description="Wireless mouse", price=25.0, stock=50)
    )
    db.add(
        models.Product(name="Monitor", description="4K Monitor", price=350.0, stock=0)
    )
    db.add(
        models.Product(
            name="Keyboard", description="Mechanical keyboard", price=80.0, stock=15
        )
    )
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


def test_search_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"].lower() == "laptop"


def test_search_by_price_range():
    response = client.get("/products/search?min_price=50&max_price=500")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Monitor and Keyboard
    names = [p["name"] for p in data]
    assert "Monitor" in names
    assert "Keyboard" in names


def test_search_in_stock():
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Laptop, Mouse, Keyboard (Monitor has 0 stock)
    for p in data:
        assert p["stock"] > 0


def test_search_combined():
    response = client.get("/products/search?q=m&min_price=20&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert (
        len(data) == 1
    )  # Mouse (Monitor is out of stock, Keyboard doesn't have 'm' in name)
    assert data[0]["name"] == "Mouse"
