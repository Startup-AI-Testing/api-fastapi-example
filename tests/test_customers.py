import pytest

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
    assert "Email already registered" in response.json()["detail"]

def test_read_customers(client):
    client.post("/customers/", json={"name": "C1", "email": "c1@example.com"})
    client.post("/customers/", json={"name": "C2", "email": "c2@example.com"})
    
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_read_customer_by_id(client):
    create_res = client.post("/customers/", json={"name": "C3", "email": "c3@example.com"})
    customer_id = create_res.json()["id"]
    
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "C3"

def test_read_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404
