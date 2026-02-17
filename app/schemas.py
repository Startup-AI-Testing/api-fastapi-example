from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Item schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    unit_price: float

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    customer_name: str
    customer_email: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None


class Order(OrderBase):
    id: int
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True


# Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity_available: int
    quantity_reserved: int
    quantity_sold: int
    reorder_point: int


class Inventory(InventoryBase):
    version: int
    last_restocked_at: Optional[datetime]

    class Config:
        from_attributes = True


class StockReservationBase(BaseModel):
    product_id: int
    quantity: int
    reservation_type: str = "order"


class StockReservationCreate(StockReservationBase):
    pass


class StockReservation(BaseModel):
    id: UUID
    inventory_id: int
    order_id: Optional[int]
    quantity: int
    reserved_at: datetime
    expires_at: datetime
    status: str
    reservation_type: str

    class Config:
        from_attributes = True


class StockReservationConfirm(BaseModel):
    order_id: int


class RestockRequest(BaseModel):
    product_id: int
    quantity: int


class StockAdjustmentRequest(BaseModel):
    product_id: int
    quantity: int
    reason: str


class StockMovement(BaseModel):
    id: UUID
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[UUID]
    created_at: datetime
    created_by: str

    class Config:
        from_attributes = True
