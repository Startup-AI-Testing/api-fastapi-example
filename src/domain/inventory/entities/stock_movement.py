from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class StockMovement:
    id: uuid.UUID
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[uuid.UUID]
    created_at: datetime
    created_by: str

    @classmethod
    def create(
        cls,
        id: uuid.UUID,
        inventory_id: int,
        movement_type: str,
        quantity: int,
        reference_id: Optional[uuid.UUID] = None,
        created_by: str = "system"
    ) -> "StockMovement":
        return cls(
            id=id,
            inventory_id=inventory_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_id=reference_id,
            created_at=datetime.utcnow(),
            created_by=created_by
        )
