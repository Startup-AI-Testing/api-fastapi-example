import pytest
import uuid
from unittest.mock import Mock
from src.application.handlers.inventory.release_expired_reservations_handler import ReleaseExpiredReservationsHandler
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_release_expired_reservations_handler():
    # Arrange
    service = Mock(spec=InventoryDomainService)
    repo = Mock(spec=IStockReservationRepository)
    handler = ReleaseExpiredReservationsHandler(service, repo)
    
    res1 = Mock(spec=StockReservation)
    res1.id = uuid.uuid4()
    res2 = Mock(spec=StockReservation)
    res2.id = uuid.uuid4()
    
    repo.get_expired_reservations.return_value = [res1, res2]
    
    # Act
    handler.execute()
    
    # Assert
    assert service.release_reservation.call_count == 2
    service.release_reservation.assert_any_call(res1.id, reason="expired")
    service.release_reservation.assert_any_call(res2.id, reason="expired")
