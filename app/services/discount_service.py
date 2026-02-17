from datetime import datetime
from decimal import Decimal
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models

class DiscountService:
    def __init__(self, db: Session):
        self.db = db

    def validate_discount(self, code: str, order_amount: Decimal) -> Tuple[bool, str, Optional[models.Discount]]:
        db_discount = self.db.query(models.Discount).filter(models.Discount.code == code).first()
        
        if not db_discount:
            return False, "Discount code not found", None
        
        try:
            self.validate_discount_object(db_discount, order_amount)
        except HTTPException as e:
            return False, e.detail, None
        
        return True, "Discount is valid", db_discount

    @staticmethod
    def validate_discount_object(discount: models.Discount, order_amount: Decimal) -> None:
        if not discount.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount is inactive")
        
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount is not yet valid")
        
        if discount.valid_until and now > discount.valid_until:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount has expired")
        
        if discount.max_uses and discount.current_uses >= discount.max_uses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discount has reached maximum uses")
        
        if order_amount < discount.min_order_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Minimum order amount of {discount.min_order_amount} not met"
            )

    @staticmethod
    def calculate_discount(discount: models.Discount, order_subtotal: Decimal) -> Decimal:
        if discount.discount_type == "percentage":
            discount_amount = (order_subtotal * Decimal(str(discount.discount_value))) / Decimal("100.0")
        else:  # fixed_amount
            discount_amount = Decimal(str(discount.discount_value))
        
        # Discount cannot exceed subtotal
        return min(discount_amount, order_subtotal)
