from datetime import datetime, timedelta


def test_create_discount(client):
    response = client.post(
        "/discounts/",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 100.0,
            "max_uses": 10,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "SUMMER2024"
    assert data["discount_value"] == 20.0


def test_list_discounts(client):
    # Create a discount
    client.post(
        "/discounts/",
        json={
            "code": "SUMMER2024",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        },
    )

    response = client.get("/discounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(d["code"] == "SUMMER2024" for d in data)


def test_validate_discount(client):
    # Create a discount
    client.post(
        "/discounts/",
        json={
            "code": "VALID20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_amount": 50.0,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
        },
    )

    # Validate valid discount
    response = client.post("/discounts/VALID20/validate?order_amount=100")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 20.0

    # Validate non-existent discount
    response = client.post("/discounts/NONEXISTENT/validate")
    assert response.status_code == 404


def test_toggle_discount(client):
    # Create a discount
    client.post(
        "/discounts/",
        json={
            "code": "TOGGLE",
            "discount_type": "fixed_amount",
            "discount_value": 10.0,
            "valid_from": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True,
        },
    )

    # Deactivate
    response = client.put("/discounts/TOGGLE", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Activate
    response = client.put("/discounts/TOGGLE", json={"is_active": True})
    assert response.status_code == 200
    assert response.json()["is_active"] is True
