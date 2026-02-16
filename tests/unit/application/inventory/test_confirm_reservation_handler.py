import pytest
from unittest.mock import MagicMock, patch
from src.application.inventory.handlers.confirm_reservation_handler import ConfirmReservationHandler
from uuid import uuid4

def test_confirm_reservation_handler_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_event_publisher = MagicMock()
    
    reservation_id = uuid4()
    order_id = uuid4()
    
    with patch("src.application.inventory.handlers.confirm_reservation_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        
        handler = ConfirmReservationHandler(mock_uow, mock_event_publisher)
        
        # Act
        handler.execute(reservation_id=reservation_id, order_id=order_id)
        
        # Assert
        mock_service.confirm_reservation.assert_called_once_with(reservation_id, order_id)
        mock_uow.commit.assert_called_once()
