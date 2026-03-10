import pytest
from app import models
import uuid

def test_reserve_stock_endpoint(client, db):
    # Create product
    p = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    # Initialize inventory (normally this would be done by a service or migration)
    # For now, we'll assume the endpoint handles it or we create it here
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    from src.domain.inventory.entities.inventory import Inventory as DomainInventory
    repo = SqlInventoryRepository(db)
    repo.save(DomainInventory.create(product_id=p.id, quantity_available=10))
    
    response = client.post("/inventory/reserve", json={
        "product_id": p.id,
        "quantity": 2,
        "reservation_type": "cart"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 2
    assert data["status"] == "active"
    assert "id" in data

def test_confirm_reservation_endpoint(client, db):
    # Setup: product, inventory
    p = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository, SqlStockReservationRepository, SqlStockMovementRepository
    from src.domain.inventory.entities.inventory import Inventory as DomainInventory
    from src.domain.inventory.services.inventory_service import InventoryDomainService
    from src.domain.inventory.ports.inventory_ports import IEventPublisher
    
    class DummyPublisher(IEventPublisher):
        def publish(self, event): pass

    inv_repo = SqlInventoryRepository(db)
    res_repo = SqlStockReservationRepository(db)
    mov_repo = SqlStockMovementRepository(db)
    service = InventoryDomainService(inv_repo, res_repo, mov_repo, DummyPublisher())
    
    inv_repo.save(DomainInventory.create(product_id=p.id, quantity_available=10))
    
    # Reserve stock via service
    res = service.reserve_stock(p.id, 2, "cart")
    
    order_id = str(uuid.uuid4())
    response = client.post(f"/inventory/reserve/{res.id}/confirm", json={
        "order_id": order_id
    })
    
    assert response.status_code == 200
    
    # Verify reservation is confirmed
    res_db = res_repo.get_by_id(res.id)
    assert res_db.status == "confirmed"
    assert str(res_db.order_id) == order_id
    
    # Verify inventory updated
    inv_db = inv_repo.get_by_product_id(p.id)
    assert inv_db.quantity_reserved == 0
    assert inv_db.quantity_sold == 2
    assert inv_db.quantity_available == 8

def test_restock_endpoint(client, db):
    p = models.Product(name="Test Product", price=10.0, stock=10)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
    from src.domain.inventory.entities.inventory import Inventory as DomainInventory
    repo = SqlInventoryRepository(db)
    repo.save(DomainInventory.create(product_id=p.id, quantity_available=10))
    
    response = client.post("/inventory/restock", json={
        "product_id": p.id,
        "quantity": 5,
        "reference": "RESTOCK-001"
    })
    
    assert response.status_code == 200
    
    inv = repo.get_by_product_id(p.id)
    assert inv.quantity_available == 15
