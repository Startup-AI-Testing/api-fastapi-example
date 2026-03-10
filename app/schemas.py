from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid


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


# Inventory schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity_available: int
    quantity_reserved: int
    quantity_sold: int
    reorder_point: int
    version: int
    last_restocked_at: Optional[datetime] = None

class Inventory(InventoryBase):
    class Config:
        from_attributes = True

class StockReservationBase(BaseModel):
    inventory_id: int
    quantity: int
    reservation_type: str

class StockReservationCreate(BaseModel):
    product_id: int
    quantity: int
    reservation_type: str

class StockReservation(StockReservationBase):
    id: str
    order_id: Optional[str] = None
    reserved_at: datetime
    expires_at: datetime
    status: str

    class Config:
        from_attributes = True

class StockReservationConfirm(BaseModel):
    order_id: str

class RestockRequest(BaseModel):
    product_id: int
    quantity: int
    reference: str

class StockAdjustment(BaseModel):
    product_id: int
    quantity: int
    reason: str

class StockMovement(BaseModel):
    id: str
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None

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
    reservation_id: Optional[str] = None


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None


class Order(OrderBase):
    id: int
    total: float
    status: str
    reservation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True
