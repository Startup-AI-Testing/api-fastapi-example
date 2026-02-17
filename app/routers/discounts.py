from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import models, schemas
from app.database import get_db
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("", response_model=schemas.Discount)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    db_discount = models.Discount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("", response_model=List[schemas.Discount])
def list_active_discounts(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return db.query(models.Discount).filter(
        models.Discount.is_active,
        models.Discount.valid_from <= now,
        models.Discount.valid_until >= now
    ).all()

@router.post("/{code}/validate", response_model=schemas.DiscountValidationResponse)
def validate_discount(code: str, order_amount: float, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        return schemas.DiscountValidationResponse(
            is_valid=False,
            discount_amount=0.0,
            message="Discount code not found"
        )
    
    is_valid, amount, message = DiscountService.validate_discount(discount, order_amount)
    return schemas.DiscountValidationResponse(
        is_valid=is_valid,
        discount_amount=amount,
        message=message
    )

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, status: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    discount.is_active = status.is_active
    db.commit()
    db.refresh(discount)
    return discount
