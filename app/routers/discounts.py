from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..database import get_db
from .. import models, schemas
from ..services.discount_service import DiscountService

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"],
)

class ValidateRequest(BaseModel):
    order_amount: float

@router.post("", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = models.Discount(**discount.model_dump())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("", response_model=List[schemas.Discount])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active).all()

@router.post("/{code}/validate")
def validate_discount(code: str, request: ValidateRequest, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        return {"valid": False, "error": "Discount code not found"}
    
    is_valid, error = DiscountService.validate_discount(discount, request.order_amount)
    return {"valid": is_valid, "error": error}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    if discount_update.is_active is not None:
        db_discount.is_active = discount_update.is_active
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
