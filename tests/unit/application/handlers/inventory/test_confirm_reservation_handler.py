import pytest
import uuid
from unittest.mock import Mock
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler, ConfirmReservationCommand
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

def test_confirm_reservation_handler():
    # Arrange
    service = Mock(spec=InventoryDomainService)
    handler = ConfirmReservationHandler(service)
    res_id = uuid.uuid4()
    command = ConfirmReservationCommand(reservation_id=res_id, order_id=123)
    
    # Act
    handler.execute(command)
    
    # Assert
    service.confirm_reservation.assert_called_once_with(
        reservation_id=res_id,
        order_id=123
    )
