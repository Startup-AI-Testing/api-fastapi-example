from app import models
from datetime import datetime, timedelta

def test_get_order_stats_empty(client, db):
    response = client.get("/orders/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 0
    assert data["total_revenue"] == 0.0
    assert data["average_order_value"] == 0.0
    assert data["top_product_id"] is None

def test_get_order_stats_with_data(client, db):
    # Create products
    p1 = models.Product(name="Product 1", price=10.0, stock=100)
    p2 = models.Product(name="Product 2", price=20.0, stock=100)
    db.add_all([p1, p2])
    db.commit()

    # Create orders
    o1 = models.Order(customer_name="C1", customer_email="c1@e.com", total=30.0)
    o2 = models.Order(customer_name="C2", customer_email="c2@e.com", total=40.0)
    db.add_all([o1, o2])
    db.commit()

    # Create order items
    oi1 = models.OrderItem(order_id=o1.id, product_id=p1.id, quantity=3, unit_price=10.0)
    oi2 = models.OrderItem(order_id=o2.id, product_id=p2.id, quantity=2, unit_price=20.0)
    db.add_all([oi1, oi2])
    db.commit()

    response = client.get("/orders/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 2
    assert data["total_revenue"] == 70.0
    assert data["average_order_value"] == 35.0
    assert data["top_product_id"] == p1.id # p1 has quantity 3, p2 has quantity 2

def test_get_order_stats_with_date_filter(client, db):
    # Create products
    p1 = models.Product(name="Product 1", price=10.0, stock=100)
    db.add_all([p1])
    db.commit()

    # Create orders with different dates
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    last_week = now - timedelta(days=7)

    o1 = models.Order(customer_name="C1", customer_email="c1@e.com", total=10.0, created_at=yesterday)
    o2 = models.Order(customer_name="C2", customer_email="c2@e.com", total=20.0, created_at=last_week)
    db.add_all([o1, o2])
    db.commit()

    # Filter for yesterday
    date_str = yesterday.strftime("%Y-%m-%d")
    response = client.get(f"/orders/stats?date_from={date_str}&date_to={date_str}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 1
    assert data["total_revenue"] == 10.0

def test_get_order_stats_top_product(client, db):
    # Create products
    p1 = models.Product(name="P1", price=10.0, stock=100)
    p2 = models.Product(name="P2", price=10.0, stock=100)
    db.add_all([p1, p2])
    db.commit()

    # Order 1: 2 of P1, 1 of P2
    o1 = models.Order(customer_name="C1", customer_email="c1@e.com", total=30.0)
    db.add(o1)
    db.commit()
    oi1 = models.OrderItem(order_id=o1.id, product_id=p1.id, quantity=2, unit_price=10.0)
    oi2 = models.OrderItem(order_id=o1.id, product_id=p2.id, quantity=1, unit_price=10.0)
    db.add_all([oi1, oi2])
    db.commit()

    # Order 2: 3 of P2
    o2 = models.Order(customer_name="C2", customer_email="c2@e.com", total=30.0)
    db.add(o2)
    db.commit()
    oi3 = models.OrderItem(order_id=o2.id, product_id=p2.id, quantity=3, unit_price=10.0)
    db.add(oi3)
    db.commit()

    # Total P1: 2, Total P2: 4. Top should be P2.
    response = client.get("/orders/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["top_product_id"] == p2.id
