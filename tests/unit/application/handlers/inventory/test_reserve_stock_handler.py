import pytest
from unittest.mock import MagicMock
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler
from src.domain.inventory.entities.stock_reservation import StockReservation
import uuid

@pytest.fixture
def mock_inventory_service():
    return MagicMock()

@pytest.fixture
def handler(mock_inventory_service):
    return ReserveStockHandler(inventory_service=mock_inventory_service)

def test_reserve_stock_handler_success(handler, mock_inventory_service):
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    mock_inventory_service.reserve_stock.return_value = reservation
    
    result = handler.execute(product_id=1, quantity=2, reservation_type="cart")
    
    assert result == reservation
    mock_inventory_service.reserve_stock.assert_called_once_with(1, 2, "cart")
