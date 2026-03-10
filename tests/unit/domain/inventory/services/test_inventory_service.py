import pytest
from unittest.mock import MagicMock
from src.domain.inventory.services.inventory_service import InventoryDomainService
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
import uuid

@pytest.fixture
def mock_inventory_repo():
    return MagicMock()

@pytest.fixture
def mock_reservation_repo():
    return MagicMock()

@pytest.fixture
def mock_movement_repo():
    return MagicMock()

@pytest.fixture
def mock_event_publisher():
    return MagicMock()

@pytest.fixture
def inventory_service(mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    return InventoryDomainService(
        inventory_repo=mock_inventory_repo,
        reservation_repo=mock_reservation_repo,
        movement_repo=mock_movement_repo,
        event_publisher=mock_event_publisher
    )

def test_reserve_stock_success(inventory_service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo):
    inventory = Inventory.create(product_id=1, quantity_available=10)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    reservation = inventory_service.reserve_stock(product_id=1, quantity=2, reservation_type="cart")
    
    assert reservation.quantity == 2
    assert inventory.quantity_available == 8
    assert inventory.quantity_reserved == 2
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once()
    mock_movement_repo.save.assert_called_once()

def test_reserve_stock_insufficient(inventory_service, mock_inventory_repo):
    inventory = Inventory.create(product_id=1, quantity_available=5)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    with pytest.raises(ValueError, match="Insufficient stock"):
        inventory_service.reserve_stock(product_id=1, quantity=6)

def test_confirm_reservation_success(inventory_service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo):
    inventory = Inventory(product_id=1, quantity_available=8, quantity_reserved=2)
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    
    mock_reservation_repo.get_by_id.return_value = reservation
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    inventory_service.confirm_reservation(reservation_id=reservation.id, order_id=101)
    
    assert reservation.status == "confirmed"
    assert reservation.order_id == 101
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 2
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once_with(reservation)
    mock_movement_repo.save.assert_called_once()
