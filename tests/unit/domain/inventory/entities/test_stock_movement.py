import uuid
from datetime import datetime
from src.domain.inventory.entities.stock_movement import StockMovement

def test_stock_movement_creation():
    movement_id = uuid.uuid4()
    reference_id = uuid.uuid4()
    movement = StockMovement.create(
        id=movement_id,
        inventory_id=1,
        movement_type="restock",
        quantity=50,
        reference_id=reference_id,
        created_by="admin"
    )
    assert movement.id == movement_id
    assert movement.inventory_id == 1
    assert movement.movement_type == "restock"
    assert movement.quantity == 50
    assert movement.reference_id == reference_id
    assert movement.created_by == "admin"
    assert isinstance(movement.created_at, datetime)
