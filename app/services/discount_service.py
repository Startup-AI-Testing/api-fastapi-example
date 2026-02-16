from datetime import datetime
from fastapi import HTTPException
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        if not discount.is_active:
            raise HTTPException(status_code=400, detail="Discount code is inactive")
        
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise HTTPException(status_code=400, detail="Discount code is not yet valid")
        
        if discount.valid_until and now > discount.valid_until:
            raise HTTPException(status_code=400, detail="Discount code has expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise HTTPException(status_code=400, detail="Discount code has reached its usage limit")
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Order amount {order_amount} is below the minimum required {discount.min_order_amount}"
            )

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return (order_amount * discount.discount_value) / 100
        elif discount.discount_type == "fixed_amount":
            return float(discount.discount_value)
        return 0.0
