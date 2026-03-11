from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
import uuid

@dataclass
class StockMovement:
    id: uuid.UUID
    inventory_id: int
    movement_type: str  # "restock", "reserve", "release", "sale", "adjustment"
    quantity: int
    reference_id: Optional[str]
    created_at: datetime
    created_by: str

    @classmethod
    def create(
        cls,
        inventory_id: int,
        movement_type: str,
        quantity: int,
        reference_id: Optional[Any] = None,
        created_by: str = "system"
    ) -> "StockMovement":
        return cls(
            id=uuid.uuid4(),
            inventory_id=inventory_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_id=str(reference_id) if reference_id else None,
            created_at=datetime.utcnow(),
            created_by=created_by
        )
