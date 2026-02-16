from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.discount_service import DiscountService
from pydantic import BaseModel

router = APIRouter(prefix="/discounts", tags=["discounts"])

class ValidateRequest(BaseModel):
    order_amount: float

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
    return db.query(models.Discount).filter(models.Discount.is_active == True).all()

@router.post("/{code}/validate")
def validate_discount(code: str, request: ValidateRequest, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        return {"valid": False, "error": "Discount not found"}
    
    is_valid, error = DiscountService.validate_discount(discount, request.order_amount)
    return {"valid": is_valid, "error": error}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    if update.is_active is not None:
        discount.is_active = update.is_active
        
    db.commit()
    db.refresh(discount)
    return discount
