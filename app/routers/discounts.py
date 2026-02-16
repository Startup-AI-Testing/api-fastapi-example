from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    new_discount = models.Discount(**discount.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("", response_model=List[schemas.Discount])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active).all()

@router.post("/{code}/validate")
def validate_discount(code: str, order_amount: float, db: Session = Depends(get_db)):
    """Validate a discount code for a given order amount."""
    discount = DiscountService.validate_discount(db, code, order_amount)
    
    if discount.discount_type == "percentage":
        discount_amount = (order_amount * discount.discount_value) / 100
    else:
        discount_amount = float(discount.discount_value)
        
    discount_amount = min(discount_amount, order_amount)
    
    return {
        "valid": True,
        "discount_code": code,
        "discount_amount": discount_amount,
        "new_total": order_amount - discount_amount
    }

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, status_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    discount.is_active = status_update.is_active
    db.commit()
    db.refresh(discount)
    return discount
