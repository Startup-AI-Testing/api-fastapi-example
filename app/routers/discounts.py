from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Discount
from app.schemas import DiscountCreate, DiscountRead, DiscountUpdate
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("", response_model=DiscountRead, status_code=status.HTTP_201_CREATED)
def create_discount(discount: DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(Discount).filter(Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    new_discount = Discount(**discount.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("", response_model=List[DiscountRead])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(Discount).filter(Discount.is_active).all()

@router.post("/{code}/validate")
def validate_discount(code: str, subtotal: float, db: Session = Depends(get_db)):
    discount = db.query(Discount).filter(Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    try:
        DiscountService.validate_discount(discount, subtotal)
        amount = DiscountService.calculate_discount_amount(discount, subtotal)
        return {"valid": True, "discount_amount": amount}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{code}", response_model=DiscountRead)
def update_discount(code: str, discount_update: DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = db.query(Discount).filter(Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    update_data = discount_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_discount, key, value)
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
