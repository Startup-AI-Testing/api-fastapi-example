from datetime import datetime
import uuid
from src.domain.inventory.entities.stock_movement import StockMovement

def test_stock_movement_creation():
    ref_id = str(uuid.uuid4())
    movement = StockMovement.create(
        inventory_id=1,
        movement_type="restock",
        quantity=10,
        reference_id=ref_id,
        created_by="admin"
    )
    assert isinstance(movement.id, str)
    assert movement.inventory_id == 1
    assert movement.movement_type == "restock"
    assert movement.quantity == 10
    assert movement.reference_id == ref_id
    assert movement.created_by == "admin"
    assert isinstance(movement.created_at, datetime)
