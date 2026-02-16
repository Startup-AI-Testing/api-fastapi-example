from datetime import datetime
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, subtotal: float) -> None:
        if not discount.is_active:
            raise ValueError("Discount is not active")
        
        now = datetime.now()
        if discount.valid_from and now < discount.valid_from:
            raise ValueError("Discount is not yet valid")
        
        if discount.valid_until and now > discount.valid_until:
            raise ValueError("Discount has expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise ValueError("Discount usage limit reached")
        
        if discount.min_order_amount and subtotal < discount.min_order_amount:
            raise ValueError("Order amount does not meet minimum requirement")

    @staticmethod
    def calculate_discount_amount(discount: Discount, subtotal: float) -> float:
        if discount.discount_type == "percentage":
            amount = subtotal * (discount.discount_value / 100.0)
        elif discount.discount_type == "fixed_amount":
            amount = discount.discount_value
        else:
            amount = 0.0
            
        return min(amount, subtotal)
