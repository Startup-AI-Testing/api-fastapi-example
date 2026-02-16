import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Product, Discount

client = TestClient(app)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Create a product
        product = Product(name="Test Product", price=100.0, stock=10)
        db.add(product)
        # Create a discount
        discount = Discount(
            code="SUMMER20",
            discount_type="percentage",
            discount_value=20.0,
            min_order_amount=50.0,
            is_active=True,
            max_uses=10,
            current_uses=0
        )
        db.add(discount)
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_order_with_discount(db):
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": 1, "quantity": 2}],
            "discount_code": "SUMMER20"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 200.0
    assert data["discount_code"] == "SUMMER20"
    assert data["discount_amount"] == 40.0
    assert data["total"] == 160.0
    
    # Verify discount uses increased
    discount = db.query(Discount).filter(Discount.code == "SUMMER20").first()
    assert discount.current_uses == 1

def test_create_order_with_invalid_discount(db):
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": 1, "quantity": 1}],
            "discount_code": "INVALID"
        }
    )
    assert response.status_code == 404

def test_create_order_with_insufficient_amount(db):
    # Create a discount with high min amount
    client.post(
        "/discounts",
        json={
            "code": "HIGHMIN",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "min_order_amount": 500.0
        }
    )
    
    response = client.post(
        "/orders",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "items": [{"product_id": 1, "quantity": 1}],
            "discount_code": "HIGHMIN"
        }
    )
    assert response.status_code == 400
    assert "minimum" in response.json()["detail"]
