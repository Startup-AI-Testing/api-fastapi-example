import pytest
from unittest.mock import MagicMock
from src.application.handlers.inventory.restock_handler import RestockHandler

@pytest.fixture
def mock_inventory_service():
    return MagicMock()

@pytest.fixture
def handler(mock_inventory_service):
    return RestockHandler(inventory_service=mock_inventory_service)

def test_restock_handler_success(handler, mock_inventory_service):
    handler.execute(product_id=1, quantity=10, reference="RESTOCK-001")
    
    mock_inventory_service.restock.assert_called_once_with(1, 10, "RESTOCK-001")
