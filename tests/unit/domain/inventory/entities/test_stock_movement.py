from datetime import datetime
from uuid import uuid4
from src.domain.inventory.entities.stock_movement import StockMovement

def test_create_stock_movement():
    inventory_id = 1
    quantity = 10
    movement_type = "restock"
    reference_id = uuid4()
    created_by = "admin"
    
    movement = StockMovement.create(
        inventory_id=inventory_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_id=reference_id,
        created_by=created_by
    )
    
    assert movement.inventory_id == inventory_id
    assert movement.movement_type == movement_type
    assert movement.quantity == quantity
    assert movement.reference_id == str(reference_id)
    assert movement.created_by == created_by
    assert isinstance(movement.created_at, datetime)
    assert isinstance(movement.id, uuid4().__class__)
