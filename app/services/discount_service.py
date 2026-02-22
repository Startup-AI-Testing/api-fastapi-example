from datetime import datetime
from typing import Tuple, Optional
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float) -> Tuple[bool, Optional[str]]:
        if not discount.is_active:
            return False, "Discount is not active"
        
        now = datetime.utcnow()
        if now < discount.valid_from:
            return False, "Discount is not yet valid"
        
        if now > discount.valid_until:
            return False, "Discount has expired"
        
        if discount.current_uses >= discount.max_uses:
            return False, "Discount has reached its maximum uses"
        
        if order_amount < discount.min_order_amount:
            return False, "Order amount is below the minimum required for this discount"
        
        return True, None

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            amount = order_amount * (discount.discount_value / 100.0)
        elif discount.discount_type == "fixed_amount":
            amount = discount.discount_value
        else:
            amount = 0.0
            
        return min(amount, order_amount)
