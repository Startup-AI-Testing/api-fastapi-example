import pytest
from unittest.mock import MagicMock, patch
from src.application.inventory.handlers.restock_handler import RestockHandler

def test_restock_handler_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_event_publisher = MagicMock()
    
    product_id = 1
    quantity = 100
    
    with patch("src.application.inventory.handlers.restock_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        
        handler = RestockHandler(mock_uow, mock_event_publisher)
        
        # Act
        handler.execute(product_id=product_id, quantity=quantity)
        
        # Assert
        mock_service.restock.assert_called_once_with(product_id, quantity, "system")
        mock_uow.commit.assert_called_once()
