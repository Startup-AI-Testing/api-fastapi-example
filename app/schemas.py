from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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


class OrderStats(BaseModel):
    total_orders: int
    total_revenue: float
    average_order_value: float
    top_product_id: Optional[int] = None


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
