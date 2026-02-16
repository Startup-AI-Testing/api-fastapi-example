from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models


class DiscountService:
    @staticmethod
    def get_active_discount(db: Session, code: str) -> Optional[models.Discount]:
        return (
            db.query(models.Discount)
            .filter(models.Discount.code == code, models.Discount.is_active)
            .first()
        )

    @staticmethod
    def validate_discount(
        discount: models.Discount, order_amount: float
    ) -> Tuple[bool, str]:
        now = datetime.utcnow()

        if not discount.is_active:
            return False, "Discount is not active"

        if discount.valid_from > now:
            return False, "Discount is not yet valid"

        if discount.valid_until < now:
            return False, "Discount has expired"

        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            return False, "Discount has reached maximum uses"

        if order_amount < discount.min_order_amount:
            return False, f"Minimum order amount of {discount.min_order_amount} not met"

        return True, "Valid"

    @staticmethod
    def calculate_discount(discount: models.Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            amount = order_amount * (discount.discount_value / 100)
            return round(amount, 2)
        elif discount.discount_type == "fixed_amount":
            return min(discount.discount_value, order_amount)
        return 0.0

    @staticmethod
    def apply_discount(db: Session, code: str, order_amount: float) -> float:
        """
        Validates, calculates and increments usage of a discount.
        Raises HTTPException if invalid.
        """
        discount = DiscountService.get_active_discount(db, code)
        if not discount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discount code not found or inactive",
            )

        is_valid, message = DiscountService.validate_discount(discount, order_amount)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

        discount_amount = DiscountService.calculate_discount(discount, order_amount)

        # Increment uses
        discount.current_uses += 1
        db.add(discount)
        # We don't commit here, the caller (order router) will commit the whole transaction

        return discount_amount
