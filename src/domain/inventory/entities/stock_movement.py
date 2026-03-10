from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Optional

@dataclass
class StockMovement:
    id: str
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[str]
    created_at: datetime
    created_by: str

    @classmethod
    def create(cls, inventory_id: int, movement_type: str, quantity: int, reference_id: Optional[str] = None, created_by: str = "system"):
        return cls(
            id=str(uuid.uuid4()),
            inventory_id=inventory_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_id=reference_id,
            created_at=datetime.utcnow(),
            created_by=created_by
        )
