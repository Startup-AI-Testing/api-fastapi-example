from datetime import datetime
from fastapi import HTTPException, status
from app.models import Discount

class DiscountService:
    @staticmethod
    def validate_discount(discount: Discount, order_amount: float):
        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code is inactive"
            )
        
        now = datetime.utcnow()
        if discount.valid_from > now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code is not yet valid"
            )
        
        if discount.valid_until < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code has expired"
            )
        
        if discount.current_uses >= discount.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code has no uses left"
            )
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum order amount for this discount is {discount.min_order_amount}"
            )

    @staticmethod
    def calculate_discount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            discount_amount = (discount.discount_value / 100) * order_amount
        else:  # fixed_amount
            discount_amount = discount.discount_value
        
        return min(discount_amount, order_amount)
