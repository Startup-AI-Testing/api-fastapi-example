from app import models


def test_search_products_by_name(client, db):
    # Create test products
    p1 = models.Product(
        name="Laptop Pro", price=1500.0, stock=10, description="High-end laptop"
    )
    p2 = models.Product(
        name="Laptop Air", price=1000.0, stock=5, description="Lightweight laptop"
    )
    p3 = models.Product(
        name="Smartphone", price=800.0, stock=20, description="Latest smartphone"
    )
    db.add_all([p1, p2, p3])
    db.commit()

    # Search for "laptop"
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Laptop Pro" in names
    assert "Laptop Air" in names


def test_search_products_by_price_range(client, db):
    # Create test products
    p1 = models.Product(name="Cheap Item", price=10.0, stock=10)
    p2 = models.Product(name="Mid Item", price=50.0, stock=10)
    p3 = models.Product(name="Expensive Item", price=100.0, stock=10)
    db.add_all([p1, p2, p3])
    db.commit()

    # Search with price range
    response = client.get("/products/search?min_price=20&max_price=80")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Mid Item"


def test_search_products_in_stock(client, db):
    # Create test products
    p1 = models.Product(name="In Stock", price=10.0, stock=10)
    p2 = models.Product(name="Out of Stock", price=10.0, stock=0)
    db.add_all([p1, p2])
    db.commit()

    # Search for in_stock=true
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "In Stock"

    # Search for in_stock=false (should return all)
    response = client.get("/products/search?in_stock=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
