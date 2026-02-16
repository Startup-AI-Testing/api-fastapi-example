from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app import models

# Use a separate test database
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

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Seed data
    db = TestingSessionLocal()
    db.add(models.Product(name="Laptop", price=1000, stock=10))
    db.add(models.Product(name="Mouse", price=20, stock=100))
    db.add(models.Product(name="Keyboard", price=50, stock=0))
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_search_by_name():
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Laptop"

def test_search_by_price():
    response = client.get("/products/search?min_price=30&max_price=100")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Keyboard"

def test_search_in_stock():
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    assert len(response.json()) == 2
    for p in response.json():
        assert p["stock"] > 0

def test_search_combined():
    response = client.get("/products/search?q=mouse&min_price=10&in_stock=true")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Mouse"
