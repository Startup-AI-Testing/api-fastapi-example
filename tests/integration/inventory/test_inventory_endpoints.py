import pytest
from app import models

def test_reserve_stock_endpoint(client, db):
    # Create product
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    # Initialize inventory
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    response = client.post("/inventory/reserve", json={
        "product_id": product.id,
        "quantity": 2,
        "reservation_type": "cart"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["quantity"] == 2
    assert data["status"] == "active"

def test_confirm_reservation_endpoint(client, db):
    # Create product and inventory
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    # Reserve
    res_resp = client.post("/inventory/reserve", json={
        "product_id": product.id,
        "quantity": 2
    })
    reservation_id = res_resp.json()["id"]

    # Confirm
    response = client.post(f"/inventory/reserve/{reservation_id}/confirm", json={
        "order_id": 123
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"

def test_release_reservation_endpoint(client, db):
    # Create product and inventory
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    # Reserve
    res_resp = client.post("/inventory/reserve", json={
        "product_id": product.id,
        "quantity": 2
    })
    reservation_id = res_resp.json()["id"]

    # Release
    response = client.delete(f"/inventory/reserve/{reservation_id}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "released"

def test_get_inventory_by_product(client, db):
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    response = client.get(f"/inventory/product/{product.id}")
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 10

def test_restock_endpoint(client, db):
    product = models.Product(name="Test Product", price=10.0, stock=100)
    db.add(product)
    db.commit()
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    repo = SqlInventoryRepository(db)
    from src.domain.inventory.entities.inventory import Inventory
    inv = Inventory.create(product_id=product.id, quantity_available=10)
    repo.save(inv)
    db.commit()

    response = client.post("/inventory/restock", json={
        "product_id": product.id,
        "quantity": 5
    })
    
    assert response.status_code == 200
    assert response.json()["quantity_available"] == 15
