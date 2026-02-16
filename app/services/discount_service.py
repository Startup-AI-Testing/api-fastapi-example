from datetime import datetime
from typing import Optional
from app.models import Discount
from app.errors import DomainError

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float) -> None:
        if not discount.is_active:
            raise DomainError("Discount is not active")
        
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise DomainError("Discount is not yet valid")
        
        if discount.valid_until and now > discount.valid_until:
            raise DomainError("Discount has expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise DomainError("Discount has reached maximum uses")
        
        if order_amount < (discount.min_order_amount or 0):
            raise DomainError("Order amount is below the minimum required")

    @staticmethod
    def calculate_discount(discount: Discount, subtotal: float) -> float:
        if discount.discount_type == "percentage":
            amount = subtotal * (discount.discount_value / 100.0)
        elif discount.discount_type == "fixed_amount":
            amount = discount.discount_value
        else:
            amount = 0.0
        
        # Discount cannot exceed subtotal
        return min(amount, subtotal)
