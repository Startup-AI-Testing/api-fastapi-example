import pytest
from unittest.mock import MagicMock
import uuid
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation

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
def service(mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    return InventoryDomainService(
        inventory_repo=mock_inventory_repo,
        reservation_repo=mock_reservation_repo,
        movement_repo=mock_movement_repo,
        event_publisher=mock_event_publisher
    )

from src.domain.inventory.events.inventory_events import StockReserved, StockConfirmed, StockReleased

def test_reserve_stock_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    inventory = Inventory.create(product_id=1, quantity_available=100)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    reservation = service.reserve_stock(product_id=1, quantity=10, reservation_type="cart")
    
    assert inventory.quantity_available == 90
    assert inventory.quantity_reserved == 10
    assert reservation.quantity == 10
    assert reservation.inventory_id == inventory.product_id
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once()
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called()
    args, _ = mock_event_publisher.publish.call_args
    assert isinstance(args[0], StockReserved)

def test_reserve_stock_insufficient(service, mock_inventory_repo):
    inventory = Inventory.create(product_id=1, quantity_available=5)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    with pytest.raises(ValueError, match="Insufficient stock"):
        service.reserve_stock(product_id=1, quantity=10)

def test_confirm_reservation_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    inventory = Inventory.create(product_id=1, quantity_available=90, quantity_reserved=10)
    reservation = StockReservation.create(id=uuid.uuid4(), inventory_id=1, quantity=10)
    
    mock_reservation_repo.get_by_id.return_value = reservation
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    service.confirm_reservation(reservation_id=reservation.id, order_id=100)
    
    assert reservation.status == "confirmed"
    assert reservation.order_id == 100
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 10
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once_with(reservation)
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called()
    args, _ = mock_event_publisher.publish.call_args
    assert isinstance(args[0], StockConfirmed)

def test_release_reservation_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    inventory = Inventory.create(product_id=1, quantity_available=90, quantity_reserved=10)
    reservation = StockReservation.create(id=uuid.uuid4(), inventory_id=1, quantity=10)
    
    mock_reservation_repo.get_by_id.return_value = reservation
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    service.release_reservation(reservation_id=reservation.id)
    
    assert reservation.status == "released"
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_available == 100
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once_with(reservation)
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called()
    args, _ = mock_event_publisher.publish.call_args
    assert isinstance(args[0], StockReleased)

