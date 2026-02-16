from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.services.discount_service import DiscountService
from app.errors import DomainError

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = models.Discount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("", response_model=List[schemas.Discount])
def list_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active == True).all()

@router.post("/{code}/validate")
def validate_discount(code: str, validation_data: schemas.DiscountValidation, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    try:
        DiscountService.validate_discount(discount, validation_data.order_amount)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.message)
    
    return {"valid": True, "discount_code": code}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, status_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    discount.is_active = status_update.is_active
    db.commit()
    db.refresh(discount)
    return discount
