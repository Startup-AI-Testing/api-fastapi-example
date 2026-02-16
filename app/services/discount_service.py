from datetime import datetime
from app.models import Discount
from app.errors import DiscountError

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        if not discount.is_active:
            raise DiscountError("Discount code is not active")
        
        now = datetime.now()
        if discount.valid_from > now or discount.valid_until < now:
            raise DiscountError("Discount code has expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise DiscountError("Discount code has reached its maximum uses")
        
        if order_amount < discount.min_order_amount:
            raise DiscountError(f"Order amount is below the minimum required ({discount.min_order_amount})")
        
        return True

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return round(order_amount * (discount.discount_value / 100), 2)
        elif discount.discount_type == "fixed_amount":
            return float(min(discount.discount_value, order_amount))
        return 0.0
