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
    discount_code: Optional[str] = None


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None


class OrderOut(OrderBase):
    id: int
    subtotal: float
    discount_code: Optional[str] = None
    discount_amount: float
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True


class Order(OrderOut):
    pass


# Discount schemas
class DiscountBase(BaseModel):
    code: str
    discount_type: str  # "percentage" or "fixed_amount"
    discount_value: float
    min_order_amount: float = 0.0
    max_uses: Optional[int] = None
    valid_from: datetime = datetime.utcnow()
    valid_until: Optional[datetime] = None
    is_active: bool = True


class DiscountCreate(DiscountBase):
    pass


class DiscountUpdate(BaseModel):
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_amount: Optional[float] = None
    max_uses: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class DiscountOut(DiscountBase):
    id: int
    current_uses: int

    class Config:
        from_attributes = True
