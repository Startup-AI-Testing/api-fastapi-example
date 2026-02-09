def test_search_products_by_name(client):
    # Create some test products
    client.post("/products/", json={"name": "Laptop Pro", "description": "High end laptop", "price": 1500, "stock": 5})
    client.post("/products/", json={"name": "Mouse", "description": "Wireless mouse", "price": 25, "stock": 10})
    client.post("/products/", json={"name": "Laptop Case", "description": "Sleeve for laptop", "price": 30, "stock": 0})

    # Search for "laptop"
    response = client.get("/products/search?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(p["name"] == "Laptop Pro" for p in data)
    assert any(p["name"] == "Laptop Case" for p in data)

def test_search_products_by_price_range(client):
    client.post("/products/", json={"name": "A", "price": 10, "stock": 1})
    client.post("/products/", json={"name": "B", "price": 50, "stock": 1})
    client.post("/products/", json={"name": "C", "price": 100, "stock": 1})

    response = client.get("/products/search?min_price=20&max_price=60")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "B"

def test_search_products_in_stock(client):
    client.post("/products/", json={"name": "In Stock", "price": 10, "stock": 5})
    client.post("/products/", json={"name": "Out of Stock", "price": 10, "stock": 0})

    response = client.get("/products/search?in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "In Stock"

def test_search_products_combined_filters(client):
    client.post("/products/", json={"name": "Gaming Laptop", "price": 2000, "stock": 3})
    client.post("/products/", json={"name": "Office Laptop", "price": 800, "stock": 0})
    client.post("/products/", json={"name": "Budget Laptop", "price": 400, "stock": 5})

    response = client.get("/products/search?q=laptop&min_price=500&in_stock=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Gaming Laptop"
