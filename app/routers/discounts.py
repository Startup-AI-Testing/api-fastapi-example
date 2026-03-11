from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..database import get_db
from ..models import Discount
from ..schemas import DiscountCreate, DiscountUpdate, DiscountResponse
from ..services.discount_service import DiscountService, DiscountError

router = APIRouter(prefix="/discounts", tags=["discounts"])

class ValidateRequest(BaseModel):
    order_amount: float

class ValidateResponse(BaseModel):
    valid: bool
    discount_amount: float
    discount_type: str
    discount_value: float

@router.post("", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
def create_discount(discount: DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(Discount).filter(Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    new_discount = Discount(**discount.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("", response_model=List[DiscountResponse])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(Discount).filter(Discount.is_active).all()

@router.post("/{code}/validate", response_model=ValidateResponse)
def validate_discount(code: str, request: ValidateRequest, db: Session = Depends(get_db)):
    discount = db.query(Discount).filter(Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    try:
        DiscountService.validate_discount(discount, request.order_amount)
        discount_amount = DiscountService.calculate_discount(discount, request.order_amount)
        return {
            "valid": True,
            "discount_amount": discount_amount,
            "discount_type": discount.discount_type,
            "discount_value": discount.discount_value
        }
    except DiscountError as e:
        raise HTTPException(status_code=400, detail=e.message)

@router.put("/{code}", response_model=DiscountResponse)
def update_discount_status(code: str, update: DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(Discount).filter(Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    if update.is_active is not None:
        discount.is_active = update.is_active
    
    db.commit()
    db.refresh(discount)
    return discount
