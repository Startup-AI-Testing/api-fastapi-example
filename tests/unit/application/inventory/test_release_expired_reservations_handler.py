import pytest
from unittest.mock import MagicMock, patch
from src.application.inventory.handlers.release_expired_reservations_handler import ReleaseExpiredReservationsHandler
from uuid import uuid4

def test_release_expired_reservations_handler_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_event_publisher = MagicMock()
    
    expired_reservation_ids = [uuid4(), uuid4()]
    mock_uow.reservation_repo.find_expired.return_value = expired_reservation_ids
    
    with patch("src.application.inventory.handlers.release_expired_reservations_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        
        handler = ReleaseExpiredReservationsHandler(mock_uow, mock_event_publisher)
        
        # Act
        handler.execute()
        
        # Assert
        assert mock_service.release_reservation.call_count == 2
        mock_uow.commit.assert_called_once()
