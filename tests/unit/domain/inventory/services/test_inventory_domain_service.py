import pytest
from unittest.mock import Mock, MagicMock
import uuid
from datetime import datetime, timedelta
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.errors.inventory_errors import (
    InsufficientStockError, 
    InventoryNotFoundError, 
    ReservationNotFoundError
)

@pytest.fixture
def mock_inventory_repo():
    return Mock()

@pytest.fixture
def mock_reservation_repo():
    return Mock()

@pytest.fixture
def mock_movement_repo():
    return Mock()

@pytest.fixture
def mock_event_publisher():
    return Mock()

@pytest.fixture
def service(mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    return InventoryDomainService(
        inventory_repo=mock_inventory_repo,
        reservation_repo=mock_reservation_repo,
        movement_repo=mock_movement_repo,
        event_publisher=mock_event_publisher
    )

def test_reserve_stock_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    # Arrange
    product_id = 1
    quantity = 2
    inventory = Inventory.create(product_id=product_id, quantity_available=10)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    # Act
    reservation = service.reserve_stock(product_id, quantity)
    
    # Assert
    assert reservation.quantity == quantity
    assert inventory.quantity_available == 8
    assert inventory.quantity_reserved == 2
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once()
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called_once()

def test_reserve_stock_insufficient(service, mock_inventory_repo):
    # Arrange
    product_id = 1
    quantity = 10
    inventory = Inventory.create(product_id=product_id, quantity_available=5)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    # Act & Assert
    with pytest.raises(InsufficientStockError):
        service.reserve_stock(product_id, quantity)

def test_confirm_reservation_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    # Arrange
    product_id = 1
    inventory = Inventory.create(product_id=product_id, quantity_available=8, quantity_reserved=2)
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    
    mock_reservation_repo.get_by_id.return_value = reservation
    mock_inventory_repo.get_by_product_id.return_value = inventory # Assuming we get by product_id or inventory_id
    # Actually service might need to get inventory by id from reservation.inventory_id
    # Let's adjust service to use inventory_repo.get_by_id if needed, or just use product_id if we have it.
    # For now let's assume service gets inventory from reservation.inventory_id
    mock_inventory_repo.get_by_id = Mock(return_value=inventory)
    
    # Act
    service.confirm_reservation(reservation.id, order_id=100)
    
    # Assert
    assert reservation.status == "confirmed"
    assert reservation.order_id == 100
    assert inventory.quantity_reserved == 0
    assert inventory.quantity_sold == 2
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once_with(reservation)
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called_once()

def test_release_reservation_success(service, mock_inventory_repo, mock_reservation_repo, mock_movement_repo, mock_event_publisher):
    # Arrange
    product_id = 1
    inventory = Inventory.create(product_id=product_id, quantity_available=8, quantity_reserved=2)
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    
    mock_reservation_repo.get_by_id.return_value = reservation
    mock_inventory_repo.get_by_id = Mock(return_value=inventory)
    
    # Act
    service.release_reservation(reservation.id, reason="cancelled")
    
    # Assert
    assert reservation.status == "released"
    assert inventory.quantity_available == 10
    assert inventory.quantity_reserved == 0
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_reservation_repo.save.assert_called_once_with(reservation)
    mock_movement_repo.save.assert_called_once()
    mock_event_publisher.publish.assert_called_once()

def test_restock_success(service, mock_inventory_repo, mock_movement_repo):
    # Arrange
    product_id = 1
    inventory = Inventory.create(product_id=product_id, quantity_available=10)
    mock_inventory_repo.get_by_product_id.return_value = inventory
    
    # Act
    service.restock(product_id, 5)
    
    # Assert
    assert inventory.quantity_available == 15
    mock_inventory_repo.save.assert_called_once_with(inventory)
    mock_movement_repo.save.assert_called_once()
