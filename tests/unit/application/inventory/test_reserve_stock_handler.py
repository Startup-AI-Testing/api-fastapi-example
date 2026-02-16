import pytest
from unittest.mock import MagicMock, patch
from src.application.inventory.handlers.reserve_stock_handler import ReserveStockHandler
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_reserve_stock_handler_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.__exit__.return_value = None
    mock_event_publisher = MagicMock()
    
    # Mock repositories on UoW
    mock_uow.inventory_repo = MagicMock()
    mock_uow.reservation_repo = MagicMock()
    mock_uow.movement_repo = MagicMock()
    
    reservation = MagicMock(spec=StockReservation)
    
    with patch("src.application.inventory.handlers.reserve_stock_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        mock_service.reserve_stock.return_value = reservation
        
        handler = ReserveStockHandler(mock_uow, mock_event_publisher)
        
        # Act
        result = handler.execute(product_id=1, quantity=5, reservation_type="order")
        
        # Assert
        assert result == reservation
        mock_service.reserve_stock.assert_called_once_with(1, 5, "order")
        mock_uow.commit.assert_called_once()

def test_reserve_stock_handler_retry_on_conflict():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.__exit__.return_value = None
    mock_event_publisher = MagicMock()
    
    with patch("src.application.inventory.handlers.reserve_stock_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        # Fail twice with conflict, then succeed
        mock_service.reserve_stock.side_effect = [
            Exception("Concurrency conflict"),
            Exception("Concurrency conflict"),
            MagicMock(spec=StockReservation)
        ]
        
        handler = ReserveStockHandler(mock_uow, mock_event_publisher)
        
        # Act
        result = handler.execute(product_id=1, quantity=5)
        
        # Assert
        assert mock_service.reserve_stock.call_count == 3
        assert mock_uow.commit.call_count == 1

def test_reserve_stock_handler_fails_after_max_retries():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.__enter__.return_value = mock_uow
    mock_uow.__exit__.return_value = None
    mock_event_publisher = MagicMock()
    
    with patch("src.application.inventory.handlers.reserve_stock_handler.InventoryDomainService") as MockService:
        mock_service = MockService.return_value
        mock_service.reserve_stock.side_effect = Exception("Concurrency conflict")
        
        handler = ReserveStockHandler(mock_uow, mock_event_publisher, max_retries=3)
        
        # Act & Assert
        with pytest.raises(Exception, match="Concurrency conflict"):
            handler.execute(product_id=1, quantity=5)
        
        assert mock_service.reserve_stock.call_count == 3
