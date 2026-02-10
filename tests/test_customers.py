def test_create_customer(client):
    response = client.post(
        "/customers/",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


def test_create_customer_duplicate_email(client):
    client.post(
        "/customers/",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    response = client.post(
        "/customers/",
        json={"name": "Jane Doe", "email": "john@example.com"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_list_customers(client):
    client.post("/customers/", json={"name": "User 1", "email": "user1@example.com"})
    client.post("/customers/", json={"name": "User 2", "email": "user2@example.com"})
    
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_customer(client):
    resp = client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    customer_id = resp.json()["id"]
    
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John"


def test_get_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404


def test_get_customer_orders(client):
    # Create customer
    resp = client.post("/customers/", json={"name": "John", "email": "john@example.com"})
    customer_id = resp.json()["id"]
    
    # Create product
    client.post("/products/", json={"name": "Product 1", "price": 100, "stock": 10})
    
    # Create order
    client.post("/orders/", json={
        "customer_id": customer_id,
        "items": [{"product_id": 1, "quantity": 1}]
    })
    
    response = client.get(f"/customers/{customer_id}/orders")
    assert response.status_code == 200
    assert len(response.json()) == 1
