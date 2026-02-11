from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


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


# Customer schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    created_at: datetime

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
    order_id: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    customer_id: int


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: OrderStatus


class Order(OrderBase):
    id: int
    status: OrderStatus
    total: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True
