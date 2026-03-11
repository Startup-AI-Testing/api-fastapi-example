import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.adjust_stock_handler import AdjustStockHandler

def test_adjust_stock_handler():
    service = Mock()
    handler = AdjustStockHandler(service)
    
    handler.execute(product_id=1, quantity=-5, reason="Damaged")
    
    service.adjust_stock.assert_called_once_with(
        product_id=1, 
        quantity=-5, 
        reason="Damaged"
    )
