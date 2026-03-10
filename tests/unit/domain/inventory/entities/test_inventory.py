from datetime import datetime
import pytest
from src.domain.inventory.entities.inventory import Inventory

def test_inventory_creation():
    inventory = Inventory.create(
        product_id=1,
        quantity_available=10,
        reorder_point=5
    )
    assert inventory.product_id == 1
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 0
    assert inventory.reorder_point == 5
    assert inventory.version == 1
    assert isinstance(inventory.last_restocked_at, datetime)

def test_inventory_reserve_stock():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve(2)
    assert inventory.quantity_available == 8
    assert inventory.quantity_reserved == 2

def test_inventory_reserve_insufficient_stock():
    inventory = Inventory.create(product_id=1, quantity_available=5)
    with pytest.raises(ValueError, match="Insufficient stock"):
        inventory.reserve(6)

def test_inventory_confirm_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve(2)
    inventory.confirm_reservation(2)
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 2
    assert inventory.quantity_available == 8

def test_inventory_release_reservation():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve(2)
    inventory.release_reservation(2)
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_available == 10

def test_inventory_restock():
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.restock(5)
    assert inventory.quantity_available == 15
