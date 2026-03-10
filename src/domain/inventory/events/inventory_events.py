from dataclasses import dataclass
import uuid

@dataclass
class StockReserved:
    product_id: int
    quantity: int
    reservation_id: uuid.UUID

@dataclass
class StockConfirmed:
    product_id: int
    quantity: int
    order_id: int

@dataclass
class StockReleased:
    product_id: int
    quantity: int
    reason: str

@dataclass
class LowStockDetected:
    product_id: int
    quantity_available: int
    reorder_point: int

@dataclass
class OutOfStock:
    product_id: int
