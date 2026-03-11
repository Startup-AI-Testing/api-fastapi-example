import pytest
from datetime import datetime
from src.domain.inventory.entities.inventory import Inventory

def test_create_inventory():
    product_id = 1
    inventory = Inventory.create(
        product_id=product_id,
        quantity_available=10,
        reorder_point=5
    )
    
    assert inventory.product_id == product_id
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 0
    assert inventory.reorder_point == 5
    assert inventory.version == 1
    assert isinstance(inventory.last_restocked_at, datetime)

def test_inventory_reserve_stock_success():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve_stock(3)
    
    assert inventory.quantity_available == 7
    assert inventory.quantity_reserved == 3

def test_inventory_reserve_stock_insufficient():
    inventory = Inventory.create(product_id=1, quantity_available=2)
    with pytest.raises(ValueError, match="Insufficient stock"):
        inventory.reserve_stock(3)

def test_inventory_confirm_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve_stock(3)
    inventory.confirm_reservation(3)
    
    assert inventory.quantity_available == 7
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 3

def test_inventory_release_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve_stock(3)
    inventory.release_reservation(3)
    
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0

def test_inventory_restock():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.restock(5)
    
    assert inventory.quantity_available == 15
