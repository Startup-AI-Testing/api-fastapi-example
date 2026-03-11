import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.restock_handler import RestockHandler

def test_restock_handler_success():
    service = Mock()
    handler = RestockHandler(service)
    
    handler.execute(product_id=1, quantity=100, reference="PO-123")
    
    service.restock.assert_called_once_with(
        product_id=1, 
        quantity=100, 
        reference="PO-123"
    )

def test_restock_handler_error():
    service = Mock()
    service.restock.side_effect = ValueError("Product not found")
    
    handler = RestockHandler(service)
    with pytest.raises(ValueError, match="Product not found"):
        handler.execute(product_id=1, quantity=100, reference="PO-123")
