from sqlalchemy.orm import Session
from app.models import Discount
from fastapi import HTTPException, status
from datetime import datetime

class DiscountService:
    @staticmethod
    def validate_discount(db: Session, code: str, order_amount: float) -> Discount:
        discount = db.query(Discount).filter(Discount.code == code).first()
        
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discount code {code} not found"
            )
        
        if not discount.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code is inactive"
            )
        
        now = datetime.utcnow()
        if now < discount.valid_from or now > discount.valid_until:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code has expired or is not yet valid"
            )
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount code has reached its maximum number of uses"
            )
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order amount {order_amount} is below the minimum required {discount.min_order_amount} for this discount"
            )
        
        return discount

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            amount = (discount.discount_value / 100.0) * order_amount
        else:  # fixed_amount
            amount = discount.discount_value
        
        # Discount cannot exceed order amount
        return min(amount, order_amount)

    @staticmethod
    def increment_usage(db: Session, discount: Discount):
        discount.current_uses += 1
        db.add(discount)
        db.commit()
        db.refresh(discount)
