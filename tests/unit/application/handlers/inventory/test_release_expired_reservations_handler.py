import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.release_expired_reservations_handler import ReleaseExpiredReservationsHandler

def test_release_expired_reservations_handler():
    service = Mock()
    handler = ReleaseExpiredReservationsHandler(service)
    
    handler.execute()
    
    service.release_expired_reservations.assert_called_once()
