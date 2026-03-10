import pytest
from unittest.mock import MagicMock
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler
import uuid

@pytest.fixture
def mock_inventory_service():
    return MagicMock()

@pytest.fixture
def handler(mock_inventory_service):
    return ConfirmReservationHandler(inventory_service=mock_inventory_service)

def test_confirm_reservation_handler_success(handler, mock_inventory_service):
    reservation_id = uuid.uuid4()
    order_id = uuid.uuid4()
    
    handler.execute(reservation_id=reservation_id, order_id=order_id)
    
    mock_inventory_service.confirm_reservation.assert_called_once_with(reservation_id, order_id)
