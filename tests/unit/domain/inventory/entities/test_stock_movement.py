import pytest
from datetime import datetime
import uuid
from src.domain.inventory.entities.stock_movement import StockMovement

def test_stock_movement_creation():
    inventory_id = 1
    movement_type = "restock"
    quantity = 10
    reference_id = uuid.uuid4()
    created_by = "admin"
    
    movement = StockMovement.create(
        inventory_id=inventory_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_id=reference_id,
        created_by=created_by
    )
    
    assert isinstance(movement.id, uuid.UUID)
    assert movement.inventory_id == inventory_id
    assert movement.movement_type == movement_type
    assert movement.quantity == quantity
    assert movement.reference_id == reference_id
    assert movement.created_by == created_by
    assert isinstance(movement.created_at, datetime)
