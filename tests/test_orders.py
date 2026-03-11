from datetime import datetime, timedelta
from app import models

def test_get_order_stats_empty(client):
    response = client.get("/orders/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 0
    assert data["total_revenue"] == 0.0
    assert data["average_order_value"] == 0.0
    assert data["top_product_id"] is None

def test_get_order_stats(client, db):
    # Create products
    p1 = models.Product(name="P1", price=10.0, stock=100)
    p2 = models.Product(name="P2", price=20.0, stock=100)
    db.add(p1)
    db.add(p2)
    db.commit()
    db.refresh(p1)
    db.refresh(p2)

    # Create orders
    # Order 1: yesterday, P1 (qty 2)
    o1 = models.Order(
        customer_name="C1",
        customer_email="c1@example.com",
        total=20.0,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    o1.items = [models.OrderItem(product_id=p1.id, quantity=2, unit_price=10.0)]
    
    # Order 2: today, P2 (qty 1)
    o2 = models.Order(
        customer_name="C2",
        customer_email="c2@example.com",
        total=20.0,
        created_at=datetime.utcnow()
    )
    o2.items = [models.OrderItem(product_id=p2.id, quantity=1, unit_price=20.0)]
    
    # Order 3: today, P1 (qty 5)
    o3 = models.Order(
        customer_name="C3",
        customer_email="c3@example.com",
        total=50.0,
        created_at=datetime.utcnow()
    )
    o3.items = [models.OrderItem(product_id=p1.id, quantity=5, unit_price=10.0)]

    db.add(o1)
    db.add(o2)
    db.add(o3)
    db.commit()

    # Test stats without filter
    response = client.get("/orders/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 3
    assert data["total_revenue"] == 90.0
    assert data["average_order_value"] == 30.0
    assert data["top_product_id"] == p1.id

    # Test stats with date filter (today only)
    today = datetime.utcnow().date().isoformat()
    response = client.get(f"/orders/stats?date_from={today}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 2
    assert data["total_revenue"] == 70.0
    assert data["average_order_value"] == 35.0
    assert data["top_product_id"] == p1.id # P1 has 5, P2 has 1

    # Test stats with date filter (yesterday only)
    yesterday = (datetime.utcnow() - timedelta(days=1)).date().isoformat()
    response = client.get(f"/orders/stats?date_from={yesterday}&date_to={yesterday}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 1
    assert data["total_revenue"] == 20.0
    assert data["top_product_id"] == p1.id
