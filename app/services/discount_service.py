from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Discount
from app.errors import DiscountError

class DiscountService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def validate_and_calculate(discount: Discount, order_amount: float) -> float:
        if not discount.is_active:
            raise DiscountError("Discount is not active")
        
        now = datetime.utcnow()
        if discount.valid_from and discount.valid_from > now:
            raise DiscountError("Discount is not yet valid")
        
        if discount.valid_until and discount.valid_until < now:
            raise DiscountError("Discount is expired")
        
        if discount.max_uses is not None and discount.current_uses >= discount.max_uses:
            raise DiscountError("Discount usage limit reached")
        
        if order_amount < discount.min_order_amount:
            raise DiscountError(f"Minimum order amount not met. Required: {discount.min_order_amount}")
        
        if discount.discount_type == "percentage":
            discount_amount = order_amount * (discount.discount_value / 100)
        elif discount.discount_type == "fixed_amount":
            discount_amount = discount.discount_value
        else:
            raise DiscountError("Invalid discount type")
            
        return min(discount_amount, order_amount) # Discount cannot exceed order amount

    def validate_discount(self, code: str, order_amount: float):
        discount = self.db.query(Discount).filter(Discount.code == code).first()
        if not discount:
            return False, 0.0, "Discount code not found"
        
        try:
            amount = self.validate_and_calculate(discount, order_amount)
            return True, amount, None
        except DiscountError as e:
            return False, 0.0, str(e)
