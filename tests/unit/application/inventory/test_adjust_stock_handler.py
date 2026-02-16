import pytest
from unittest.mock import MagicMock, patch
from src.application.inventory.handlers.adjust_stock_handler import AdjustStockHandler

def test_adjust_stock_handler_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_event_publisher = MagicMock()
    
    product_id = 1
    quantity = -5
    reason = "damage"
    
    with patch("src.application.inventory.handlers.adjust_stock_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        
        handler = AdjustStockHandler(mock_uow, mock_event_publisher)
        
        # Act
        handler.execute(product_id=product_id, quantity=quantity, reason=reason)
        
        # Assert
        mock_service.adjust_stock.assert_called_once_with(product_id, quantity, reason)
        mock_uow.commit.assert_called_once()
