import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation

@pytest.fixture
def inventory_repo():
    return Mock()

@pytest.fixture
def reservation_repo():
    return Mock()

@pytest.fixture
def movement_repo():
    return Mock()

@pytest.fixture
def event_publisher():
    return Mock()

@pytest.fixture
def service(inventory_repo, reservation_repo, movement_repo, event_publisher):
    return InventoryDomainService(
        inventory_repo, 
        reservation_repo, 
        movement_repo, 
        event_publisher
    )

def test_reserve_stock_success(service, inventory_repo, reservation_repo, movement_repo):
    product_id = 1
    quantity = 5
    inventory = Inventory.create(product_id=product_id, quantity_available=10)
    inventory_repo.get_by_product_id.return_value = inventory
    
    reservation = service.reserve_stock(product_id, quantity, "cart")
    
    assert reservation.quantity == quantity
    assert inventory.quantity_available == 5
    assert inventory.quantity_reserved == 5
    inventory_repo.save.assert_called_once_with(inventory)
    reservation_repo.save.assert_called_once()
    movement_repo.save.assert_called_once()

def test_reserve_stock_insufficient(service, inventory_repo):
    product_id = 1
    quantity = 15
    inventory = Inventory.create(product_id=product_id, quantity_available=10)
    inventory_repo.get_by_product_id.return_value = inventory
    
    with pytest.raises(ValueError, match="Insufficient stock"):
        service.reserve_stock(product_id, quantity, "cart")

def test_confirm_reservation_success(service, inventory_repo, reservation_repo, movement_repo):
    inventory = Inventory.create(product_id=1, quantity_available=5)
    inventory.reserve_stock(5)
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    
    reservation_repo.get_by_id.return_value = reservation
    inventory_repo.get_by_product_id.return_value = inventory
    
    service.confirm_reservation(reservation.id, order_id=101)
    
    assert reservation.status == "confirmed"
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 5
    inventory_repo.save.assert_called_once()
    reservation_repo.save.assert_called_once()
    movement_repo.save.assert_called_once()

def test_release_reservation_success(service, inventory_repo, reservation_repo, movement_repo):
    inventory = Inventory.create(product_id=1, quantity_available=10)
    inventory.reserve_stock(5)
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    
    reservation_repo.get_by_id.return_value = reservation
    inventory_repo.get_by_product_id.return_value = inventory
    
    service.release_reservation(reservation.id, reason="cancelled")
    
    assert reservation.status == "released"
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0
    inventory_repo.save.assert_called_once()
    reservation_repo.save.assert_called_once()
    movement_repo.save.assert_called_once()
