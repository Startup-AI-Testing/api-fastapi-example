

def test_search_products_by_name(client):
    # Create some products
    client.post("/products/", json={"name": "Laptop", "price": 1000, "stock": 10})
    client.post("/products/", json={"name": "Mouse", "price": 20, "stock": 50})
    client.post("/products/", json={"name": "Keyboard", "price": 50, "stock": 0})

    # Search for "laptop"
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"


def test_search_products_by_price_range(client):
    client.post("/products/", json={"name": "Laptop", "price": 1000, "stock": 10})
    client.post("/products/", json={"name": "Mouse", "price": 20, "stock": 50})
    client.post("/products/", json={"name": "Keyboard", "price": 50, "stock": 0})

    # Search for price between 10 and 100
    response = client.get("/products/search?min_price=10&max_price=100")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Mouse" in names
    assert "Keyboard" in names


def test_search_products_in_stock(client):
    client.post("/products/", json={"name": "Laptop", "price": 1000, "stock": 10})
    client.post("/products/", json={"name": "Mouse", "price": 20, "stock": 50})
    client.post("/products/", json={"name": "Keyboard", "price": 50, "stock": 0})

    # Search for products in stock
    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [p["name"] for p in data]
    assert "Laptop" in names
    assert "Mouse" in names
    assert "Keyboard" not in names


def test_search_products_combined(client):
    client.post("/products/", json={"name": "Gaming Laptop", "price": 1500, "stock": 5})
    client.post("/products/", json={"name": "Office Laptop", "price": 800, "stock": 0})
    client.post("/products/", json={"name": "Mouse", "price": 20, "stock": 50})

    # Search for "laptop", min_price 1000, in_stock true
    response = client.get("/products/search?q=laptop&min_price=1000&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Gaming Laptop"
