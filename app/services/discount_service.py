from datetime import datetime
from typing import Optional, Tuple
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float) -> Tuple[bool, Optional[str]]:
        if not discount.is_active:
            return False, "Discount is not active"
        
        now = datetime.utcnow()
        if discount.valid_from and discount.valid_from > now:
            return False, "Discount is not yet valid"
        
        if discount.valid_until and discount.valid_until < now:
            return False, "Discount has expired"
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            return False, "Discount has reached maximum uses"
        
        if order_amount < discount.min_order_amount:
            return False, "Order amount is below minimum required for this discount"
        
        return True, None

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            discount_amount = (discount.discount_value / 100) * order_amount
        else:  # fixed_amount
            discount_amount = discount.discount_value
        
        return min(discount_amount, order_amount)
