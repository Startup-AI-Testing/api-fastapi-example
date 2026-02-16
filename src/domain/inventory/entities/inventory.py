from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Inventory:
    product_id: int
    quantity_available: int
    quantity_reserved: int
    quantity_sold: int
    reorder_point: int
    version: int
    last_restocked_at: datetime

    @property
    def id(self) -> int:
        return self.product_id

    @classmethod
    def create(
        cls,
        product_id: int,
        quantity_available: int = 0,
        reorder_point: int = 0,
        quantity_reserved: int = 0,
        quantity_sold: int = 0
    ) -> "Inventory":
        return cls(
            product_id=product_id,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            quantity_sold=quantity_sold,
            reorder_point=reorder_point,
            version=1,
            last_restocked_at=datetime.utcnow()
        )

    def can_reserve(self, quantity: int) -> bool:
        return self.quantity_available >= quantity

    def is_low_stock(self) -> bool:
        return self.quantity_available < self.reorder_point

    def reserve(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity_available < quantity:
            raise ValueError("Insufficient stock")
        
        self.quantity_available -= quantity
        self.quantity_reserved += quantity

    def confirm_reservation(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity_reserved < quantity:
            raise ValueError("Insufficient reserved stock")
        
        self.quantity_reserved -= quantity
        self.quantity_sold += quantity

    def release_reservation(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity_reserved < quantity:
            raise ValueError("Insufficient reserved stock")
        
        self.quantity_reserved -= quantity
        self.quantity_available += quantity

    def restock(self, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        self.quantity_available += quantity
        self.last_restocked_at = datetime.utcnow()

    def adjust(self, quantity: int):
        # quantity can be negative for manual adjustment down
        if self.quantity_available + quantity < 0:
            raise ValueError("Resulting stock cannot be negative")
        
        self.quantity_available += quantity
