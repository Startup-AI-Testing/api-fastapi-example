from datetime import datetime
import pytest
from src.domain.inventory.entities.inventory import Inventory

def test_inventory_creation():
    inventory = Inventory.create(
        product_id=1,
        quantity_available=100,
        reorder_point=10
    )
    assert inventory.product_id == 1
    assert inventory.quantity_available == 100
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 0
    assert inventory.reorder_point == 10
    assert inventory.version == 1
    assert isinstance(inventory.last_restocked_at, datetime)

def test_inventory_reserve_stock():
    inventory = Inventory.create(product_id=1, quantity_available=100)
    inventory.reserve(10)
    assert inventory.quantity_available == 90
    assert inventory.quantity_reserved == 10

def test_inventory_reserve_stock_insufficient():
    inventory = Inventory.create(product_id=1, quantity_available=5)
    with pytest.raises(ValueError, match="Insufficient stock"):
        inventory.reserve(10)

def test_inventory_confirm_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=100)
    inventory.reserve(10)
    inventory.confirm_reservation(10)
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 10
    assert inventory.quantity_available == 90

def test_inventory_release_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=100)
    inventory.reserve(10)
    inventory.release_reservation(10)
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_available == 100

def test_inventory_restock():
    inventory = Inventory.create(product_id=1, quantity_available=100)
    inventory.restock(50)
    assert inventory.quantity_available == 150
