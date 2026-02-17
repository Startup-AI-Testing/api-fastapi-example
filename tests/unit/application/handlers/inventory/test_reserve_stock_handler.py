import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler, ReserveStockCommand
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

def test_reserve_stock_handler():
    # Arrange
    service = Mock(spec=InventoryDomainService)
    handler = ReserveStockHandler(service)
    command = ReserveStockCommand(product_id=1, quantity=5, reservation_type="order")
    
    # Act
    handler.execute(command)
    
    # Assert
    service.reserve_stock.assert_called_once_with(
        product_id=1,
        quantity=5,
        reservation_type="order"
    )
