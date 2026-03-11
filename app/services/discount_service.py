from datetime import datetime
from app.models import Discount

class DiscountError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        now = datetime.utcnow()
        
        if not discount.is_active:
            raise DiscountError("Discount is not active")
        
        if discount.valid_from > now:
            raise DiscountError("Discount is not yet valid")
            
        if discount.valid_until < now:
            raise DiscountError("Discount has expired")
            
        if discount.max_uses > 0 and discount.current_uses >= discount.max_uses:
            raise DiscountError("Discount has reached maximum uses")
            
        if order_amount < discount.min_order_amount:
            raise DiscountError("Order amount is below the minimum required")

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return round(order_amount * (discount.discount_value / 100.0), 2)
        elif discount.discount_type == "fixed_amount":
            return min(round(discount.discount_value, 2), order_amount)
        return 0.0
