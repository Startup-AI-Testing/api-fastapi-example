from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


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


# Discount schemas
class DiscountBase(BaseModel):
    code: str
    discount_type: str  # "percentage" or "fixed_amount"
    discount_value: Decimal
    min_order_amount: Decimal = Decimal("0.0")
    max_uses: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True


class DiscountCreate(DiscountBase):
    pass


class DiscountUpdate(BaseModel):
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    max_uses: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class Discount(DiscountBase):
    id: int
    current_uses: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscountStatusUpdate(BaseModel):
    is_active: bool


class DiscountValidationRequest(BaseModel):
    order_amount: Decimal


class DiscountValidationResponse(BaseModel):
    is_valid: bool
    message: str
    discount: Optional[Discount] = None


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


class Order(OrderBase):
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
