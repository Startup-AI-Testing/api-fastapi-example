from datetime import datetime
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float) -> None:
        """
        Validates if a discount can be applied to an order.
        Raises ValueError if validation fails.
        """
        if not discount.is_active:
            raise ValueError("Discount is not active")
        
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise ValueError("Discount is not yet valid")
        
        if discount.valid_until and now > discount.valid_until:
            raise ValueError("Discount has expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise ValueError("Discount has reached maximum uses")
        
        if order_amount < discount.min_order_amount:
            raise ValueError(f"Order amount is below the minimum required ({discount.min_order_amount})")

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        """
        Calculates the discount amount.
        """
        if discount.discount_type == "percentage":
            amount = order_amount * (discount.discount_value / 100.0)
        else:  # fixed_amount
            amount = float(discount.discount_value)
        
        # Discount cannot exceed order amount
        return min(amount, order_amount)
