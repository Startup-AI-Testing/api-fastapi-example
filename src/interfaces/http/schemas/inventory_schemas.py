from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ReserveStockRequest(BaseModel):
    product_id: int
    quantity: int
    reservation_type: str

class ConfirmReservationRequest(BaseModel):
    order_id: str

class RestockRequest(BaseModel):
    product_id: int
    quantity: int
    created_by: str

class AdjustStockRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str
    created_by: str

class InventoryResponse(BaseModel):
    product_id: int
    quantity_available: int
    quantity_reserved: int
    quantity_sold: int
    reorder_point: int
    version: int
    last_restocked_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReservationResponse(BaseModel):
    id: UUID
    inventory_id: int
    order_id: Optional[str]
    quantity: int
    reserved_at: datetime
    expires_at: datetime
    status: str
    reservation_type: str

    class Config:
        from_attributes = True

class StockMovementResponse(BaseModel):
    id: UUID
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[UUID]
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True
