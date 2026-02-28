from app import models


def test_search_products_by_name(client, db):
    # Create some products
    p1 = models.Product(name="Laptop Dell", price=1000.0, stock=5)
    p2 = models.Product(name="Laptop HP", price=800.0, stock=0)
    p3 = models.Product(name="Mouse", price=20.0, stock=10)
    db.add_all([p1, p2, p3])
    db.commit()

    # Search for "laptop"
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("laptop" in item["name"].lower() for item in data)


def test_search_products_by_price_range(client, db):
    # Create some products
    p1 = models.Product(name="Laptop Dell", price=1000.0, stock=5)
    p2 = models.Product(name="Laptop HP", price=800.0, stock=0)
    p3 = models.Product(name="Mouse", price=20.0, stock=10)
    db.add_all([p1, p2, p3])
    db.commit()

    # Search for price between 500 and 900
    response = client.get("/products/search?min_price=500&max_price=900")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop HP"


def test_search_products_in_stock(client, db):
    # Create some products
    p1 = models.Product(name="Laptop Dell", price=1000.0, stock=5)
    p2 = models.Product(name="Laptop HP", price=800.0, stock=0)
    db.add_all([p1, p2])
    db.commit()

    # Search for products in stock
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop Dell"


def test_search_products_combined_filters(client, db):
    # Create some products
    p1 = models.Product(name="Laptop Dell", price=1000.0, stock=5)
    p2 = models.Product(name="Laptop HP", price=800.0, stock=0)
    p3 = models.Product(name="Laptop Apple", price=1500.0, stock=2)
    db.add_all([p1, p2, p3])
    db.commit()

    # Search for "laptop", min_price 900, in_stock=true
    response = client.get("/products/search?q=laptop&min_price=900&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [item["name"] for item in data]
    assert "Laptop Dell" in names
    assert "Laptop Apple" in names
