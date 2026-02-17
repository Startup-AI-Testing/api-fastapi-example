from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import uuid

@dataclass
class StockReservation:
    id: uuid.UUID
    inventory_id: int
    quantity: int
    reserved_at: datetime
    expires_at: datetime
    status: str = "active"
    reservation_type: str = "order"
    order_id: Optional[int] = None

    @classmethod
    def create(
        cls,
        id: uuid.UUID,
        inventory_id: int,
        quantity: int,
        reservation_type: str = "order",
        expires_in_minutes: int = 15
    ) -> "StockReservation":
        now = datetime.utcnow()
        return cls(
            id=id,
            inventory_id=inventory_id,
            quantity=quantity,
            reserved_at=now,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            status="active",
            reservation_type=reservation_type
        )

    def is_expired(self) -> bool:
        if self.status != "active":
            return False
        return datetime.utcnow() > self.expires_at

    def confirm(self, order_id: int):
        if self.status != "active":
            raise ValueError(f"Cannot confirm reservation in status {self.status}")
        if self.is_expired():
            self.status = "expired"
            raise ValueError("Reservation has expired")
        self.status = "confirmed"
        self.order_id = order_id

    def release(self):
        if self.status not in ["active", "expired"]:
             raise ValueError(f"Cannot release reservation in status {self.status}")
        self.status = "released"

    def expire(self):
        if self.status == "active":
            self.status = "expired"
