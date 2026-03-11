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

    @classmethod
    def create(
        cls, 
        product_id: int, 
        quantity_available: int = 0, 
        reorder_point: int = 10
    ) -> "Inventory":
        return cls(
            product_id=product_id,
            quantity_available=quantity_available,
            quantity_reserved=0,
            quantity_sold=0,
            reorder_point=reorder_point,
            version=1,
            last_restocked_at=datetime.utcnow()
        )

    def reserve_stock(self, quantity: int):
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

    def adjust_stock(self, quantity: int):
        # quantity can be negative for manual reduction
        new_available = self.quantity_available + quantity
        if new_available < 0:
            raise ValueError("Stock cannot be negative")
        
        self.quantity_available = new_available
