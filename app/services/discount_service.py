from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Discount
from app.errors import DiscountError

class DiscountService:
    @staticmethod
    def validate_discount(db: Session, code: str, order_amount: float) -> Discount:
        discount = db.query(Discount).filter(Discount.code == code).first()
        
        if not discount:
            raise DiscountError("Discount code not found")
        
        if not discount.is_active:
            raise DiscountError("Discount code is inactive")
        
        now = datetime.utcnow()
        if now < discount.valid_from:
            raise DiscountError("Discount code is not yet valid")
        
        if now > discount.valid_until:
            raise DiscountError("Discount code has expired")
        
        if discount.current_uses >= discount.max_uses:
            raise DiscountError("Discount code has reached maximum uses")
        
        if order_amount < discount.min_order_amount:
            raise DiscountError(f"Order amount is below the minimum required ({discount.min_order_amount})")
            
        return discount

    @staticmethod
    def calculate_discount_amount(discount: Discount, order_amount: float) -> float:
        if discount.discount_type == "percentage":
            return round(order_amount * (discount.discount_value / 100.0), 2)
        elif discount.discount_type == "fixed_amount":
            return min(discount.discount_value, order_amount)
        return 0.0
