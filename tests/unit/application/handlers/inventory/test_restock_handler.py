import pytest
from unittest.mock import Mock
from src.application.handlers.inventory.restock_handler import RestockHandler, RestockCommand
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

def test_restock_handler():
    # Arrange
    service = Mock(spec=InventoryDomainService)
    handler = RestockHandler(service)
    command = RestockCommand(product_id=1, quantity=100, created_by="admin")
    
    # Act
    handler.execute(command)
    
    # Assert
    service.restock.assert_called_once_with(
        product_id=1,
        quantity=100,
        created_by="admin"
    )
