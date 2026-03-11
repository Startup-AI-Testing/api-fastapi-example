import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_reserve_stock_handler_success():
    service = Mock()
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    service.reserve_stock.return_value = reservation
    
    handler = ReserveStockHandler(service)
    result = handler.execute(product_id=1, quantity=5)
    
    assert result == reservation
    service.reserve_stock.assert_called_once_with(
        product_id=1, 
        quantity=5, 
        reservation_type="cart"
    )

def test_reserve_stock_handler_error():
    service = Mock()
    service.reserve_stock.side_effect = ValueError("Insufficient stock")
    
    handler = ReserveStockHandler(service)
    with pytest.raises(ValueError, match="Insufficient stock"):
        handler.execute(product_id=1, quantity=5)
