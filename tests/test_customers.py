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
    # Create first customer
    client.post(
        "/customers/",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    # Create second customer with same email
    response = client.post(
        "/customers/",
        json={"name": "Jane Doe", "email": "john@example.com"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_read_customer(client):
    # Create a customer
    create_response = client.post(
        "/customers/",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    customer_id = create_response.json()["id"]

    # Read the customer
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"

def test_read_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_read_customers(client):
    # Create two customers
    client.post("/customers/", json={"name": "User 1", "email": "user1@example.com"})
    client.post("/customers/", json={"name": "User 2", "email": "user2@example.com"})

    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_read_customer_orders_empty(client):
    # Create a customer
    create_response = client.post(
        "/customers/",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    customer_id = create_response.json()["id"]

    # Get orders
    response = client.get(f"/customers/{customer_id}/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
