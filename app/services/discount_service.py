from datetime import datetime
from fastapi import HTTPException, status
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Discount code {discount.code} is inactive"
            )
        
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Discount code {discount.code} is not yet valid"
            )
        
        if discount.valid_until and now > discount.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Discount code {discount.code} has expired"
            )
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Discount code {discount.code} use limit reached"
            )
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order amount {order_amount} is below the minimum amount {discount.min_order_amount} for this discount"
            )

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return round(order_amount * (discount.discount_value / 100), 2)
        elif discount.discount_type == "fixed_amount":
            return min(float(discount.discount_value), order_amount)
        return 0.0
