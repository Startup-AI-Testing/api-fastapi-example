from datetime import datetime
from typing import Optional, Tuple
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float) -> Tuple[bool, float, Optional[str]]:
        if not discount.is_active:
            return False, 0.0, "Discount is not active"
        
        now = datetime.utcnow()
        if discount.valid_from > now:
            return False, 0.0, "Discount is not yet valid"
        
        if discount.valid_until < now:
            return False, 0.0, "Discount has expired"
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            return False, 0.0, "Discount has reached maximum uses"
        
        if order_amount < discount.min_order_amount:
            return False, 0.0, "Order amount is below the minimum required for this discount"
        
        discount_amount = 0.0
        if discount.discount_type == "percentage":
            discount_amount = order_amount * (discount.discount_value / 100.0)
        elif discount.discount_type == "fixed_amount":
            discount_amount = discount.discount_value
        
        # Ensure discount doesn't exceed order amount
        discount_amount = min(discount_amount, order_amount)
        
        return True, discount_amount, None
