from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
from typing import Optional

@dataclass
class StockReservation:
    id: str
    inventory_id: int
    quantity: int
    reserved_at: datetime
    expires_at: datetime
    status: str = "active"
    reservation_type: str = "order"
    order_id: Optional[str] = None

    @classmethod
    def create(cls, inventory_id: int, quantity: int, reservation_type: str = "order"):
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            inventory_id=inventory_id,
            quantity=quantity,
            reserved_at=now,
            expires_at=now + timedelta(minutes=15),
            reservation_type=reservation_type
        )

    def confirm(self, order_id: str):
        if self.status != "active":
            raise ValueError(f"Cannot confirm reservation in status {self.status}")
        self.status = "confirmed"
        self.order_id = order_id

    def release(self):
        if self.status != "active":
            raise ValueError(f"Cannot release reservation in status {self.status}")
        self.status = "released"

    def expire(self):
        if self.status != "active":
            raise ValueError(f"Cannot expire reservation in status {self.status}")
        self.status = "expired"

    def is_expired(self) -> bool:
        return self.status == "active" and datetime.utcnow() > self.expires_at
