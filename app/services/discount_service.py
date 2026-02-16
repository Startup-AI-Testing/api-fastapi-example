from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models

class DiscountService:
    @staticmethod
    def validate_discount(db: Session, code: str, order_amount: float) -> models.Discount:
        """Validate if a discount code can be applied to an order."""
        discount = db.query(models.Discount).filter(models.Discount.code == code).first()

        if not discount:
            raise HTTPException(status_code=400, detail="Invalid discount code")

        if not discount.is_active:
            raise HTTPException(status_code=400, detail="Discount is not active")

        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise HTTPException(status_code=400, detail="Discount is not yet valid")

        if discount.valid_until and now > discount.valid_until:
            raise HTTPException(status_code=400, detail="Discount has expired")

        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise HTTPException(status_code=400, detail="Discount usage limit reached")

        if discount.min_order_amount is not None and order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Order amount is less than minimum required ({discount.min_order_amount})"
            )

        return discount

    @staticmethod
    def calculate_discount(discount: models.Discount, order_amount: float) -> float:
        """Calculate the discount amount based on the discount type."""
        if discount.discount_type == "percentage":
            return round((order_amount * discount.discount_value) / 100, 2)
        elif discount.discount_type == "fixed_amount":
            return min(float(discount.discount_value), float(order_amount))
        return 0.0

    @staticmethod
    def apply_discount(db: Session, code: str, order_amount: float) -> float:
        """Validate and calculate discount, then increment usage."""
        discount = DiscountService.validate_discount(db, code, order_amount)
        discount_amount = DiscountService.calculate_discount(discount, order_amount)
        
        # Increment usage
        discount.current_uses += 1
        db.commit()
        
        return discount_amount

