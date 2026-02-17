from datetime import datetime
from typing import Optional, Tuple
from app.models import Discount


class DiscountService:
    @staticmethod
    def validate_discount(
        discount: Discount, order_amount: float
    ) -> Tuple[bool, Optional[str]]:
        if not discount.is_active:
            return False, "Discount is not active"

        now = datetime.utcnow()
        if not (discount.valid_from <= now <= discount.valid_until):
            return False, "Discount has expired or is not yet valid"

        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            return False, "Discount has reached its maximum uses"

        if order_amount < discount.min_order_amount:
            return (
                False,
                "Order amount is less than the minimum required for this discount",
            )

        return True, None

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            amount = (discount.discount_value / 100.0) * order_amount
        elif discount.discount_type == "fixed_amount":
            amount = discount.discount_value
        else:
            amount = 0.0

        return min(amount, order_amount)
