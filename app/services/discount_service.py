from datetime import datetime
from fastapi import HTTPException
from ..models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        if not discount.is_active:
            raise HTTPException(status_code=400, detail="Discount code is inactive")
        
        now = datetime.utcnow()
        if now < discount.valid_from:
            raise HTTPException(status_code=400, detail="Discount code is not yet valid")
        
        if now > discount.valid_until:
            raise HTTPException(status_code=400, detail="Discount code has expired")
        
        if discount.current_uses >= discount.max_uses:
            raise HTTPException(status_code=400, detail="Discount code has no uses left")
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Minimum order amount for this discount is {discount.min_order_amount}"
            )
        
        return True

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return (discount.discount_value / 100.0) * order_amount
        elif discount.discount_type == "fixed_amount":
            return min(discount.discount_value, order_amount)
        return 0.0
