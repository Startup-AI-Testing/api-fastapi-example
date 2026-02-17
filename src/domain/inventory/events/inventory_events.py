from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class StockReserved:
    product_id: int
    reservation_id: uuid.UUID
    quantity: int
    occurred_at: datetime = datetime.utcnow()

@dataclass
class StockConfirmed:
    product_id: int
    reservation_id: uuid.UUID
    order_id: int
    occurred_at: datetime = datetime.utcnow()

@dataclass
class StockReleased:
    product_id: int
    reservation_id: uuid.UUID
    reason: str
    occurred_at: datetime = datetime.utcnow()

@dataclass
class LowStockDetected:
    product_id: int
    quantity_available: int
    reorder_point: int
    occurred_at: datetime = datetime.utcnow()

@dataclass
class OutOfStock:
    product_id: int
    occurred_at: datetime = datetime.utcnow()
