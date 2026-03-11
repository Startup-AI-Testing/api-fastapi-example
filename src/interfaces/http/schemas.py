from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReserveStockRequest(BaseModel):
    product_id: int
    quantity: int
    reservation_type: str = "cart"

class ConfirmReservationRequest(BaseModel):
    order_id: int

class RestockRequest(BaseModel):
    product_id: int
    quantity: int
    reference: str

class AdjustStockRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str

class InventoryResponse(BaseModel):
    product_id: int
    quantity_available: int
    quantity_reserved: int
    quantity_sold: int
    reorder_point: int
    last_restocked_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReservationResponse(BaseModel):
    id: UUID
    inventory_id: int
    quantity: int
    status: str
    expires_at: datetime

    class Config:
        from_attributes = True

class MovementResponse(BaseModel):
    id: UUID
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
