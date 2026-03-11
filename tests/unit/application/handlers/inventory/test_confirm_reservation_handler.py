import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler

def test_confirm_reservation_handler_success():
    service = Mock()
    handler = ConfirmReservationHandler(service)
    
    handler.execute(reservation_id="uuid", order_id=10)
    
    service.confirm_reservation.assert_called_once_with(
        reservation_id="uuid", 
        order_id=10
    )

def test_confirm_reservation_handler_error():
    service = Mock()
    service.confirm_reservation.side_effect = ValueError("Reservation expired")
    
    handler = ConfirmReservationHandler(service)
    with pytest.raises(ValueError, match="Reservation expired"):
        handler.execute(reservation_id="uuid", order_id=10)
