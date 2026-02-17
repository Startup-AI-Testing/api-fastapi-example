from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Inventory:
    product_id: int
    quantity_available: int
    quantity_reserved: int = 0
    quantity_sold: int = 0
    reorder_point: int = 0
    version: int = 1
    last_restocked_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls, 
        product_id: int, 
        quantity_available: int, 
        reorder_point: int = 0,
        quantity_reserved: int = 0,
        quantity_sold: int = 0,
        version: int = 1,
        last_restocked_at: Optional[datetime] = None
    ) -> "Inventory":
        return cls(
            product_id=product_id,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            quantity_sold=quantity_sold,
            reorder_point=reorder_point,
            version=version,
            last_restocked_at=last_restocked_at or datetime.utcnow()
        )

    def reserve(self, quantity: int):
        if quantity > self.quantity_available:
            raise ValueError("Insufficient stock")
        self.quantity_available -= quantity
        self.quantity_reserved += quantity

    def confirm_reservation(self, quantity: int):
        if quantity > self.quantity_reserved:
            raise ValueError("Insufficient reserved stock")
        self.quantity_reserved -= quantity
        self.quantity_sold += quantity

    def release_reservation(self, quantity: int):
        if quantity > self.quantity_reserved:
            raise ValueError("Insufficient reserved stock to release")
        self.quantity_reserved -= quantity
        self.quantity_available += quantity

    def restock(self, quantity: int):
        self.quantity_available += quantity
        self.last_restocked_at = datetime.utcnow()

    def adjust(self, quantity: int):
        if self.quantity_available + quantity < 0:
            raise ValueError("Stock cannot be negative")
        self.quantity_available += quantity
