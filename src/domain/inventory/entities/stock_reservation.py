from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
from typing import Optional

@dataclass
class StockReservation:
    id: uuid.UUID
    inventory_id: int
    order_id: Optional[int]
    quantity: int
    reserved_at: datetime
    expires_at: datetime
    status: str # "active", "confirmed", "released", "expired"
    reservation_type: str # "order", "cart"

    @classmethod
    def create(
        cls,
        inventory_id: int,
        quantity: int,
        reservation_type: str = "order",
        expires_in_minutes: int = 15
    ) -> "StockReservation":
        now = datetime.utcnow()
        return cls(
            id=uuid.uuid4(),
            inventory_id=inventory_id,
            order_id=None,
            quantity=quantity,
            reserved_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            status="active",
            reservation_type=reservation_type
        )

    def confirm(self, order_id: int):
        if self.status != "active":
            raise ValueError(f"Cannot confirm reservation in status {self.status}")
        if self.is_expired():
            self.status = "expired"
            raise ValueError("Cannot confirm expired reservation")
        
        self.order_id = order_id
        self.status = "confirmed"

    def release(self):
        if self.status not in ["active", "confirmed"]:
             raise ValueError(f"Cannot release reservation in status {self.status}")
        self.status = "released"

    def expire(self):
        if self.status == "active":
            self.status = "expired"

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
