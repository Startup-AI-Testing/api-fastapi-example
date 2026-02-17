from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..database import get_db
from .. import models, schemas
from ..services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

class ValidationRequest(BaseModel):
    order_amount: float

class ValidationResponse(BaseModel):
    valid: bool
    discount_amount: float

@router.post("/", response_model=schemas.Discount, status_code=201)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    """Create a new discount."""
    db_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    db_discount = models.Discount(**discount.model_dump())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("/", response_model=List[schemas.Discount])
def list_discounts(db: Session = Depends(get_db)):
    """List all active discounts."""
    discounts = db.query(models.Discount).filter(models.Discount.is_active == True).all()
    return discounts

@router.post("/{code}/validate", response_model=ValidationResponse)
def validate_discount(code: str, request: ValidationRequest, db: Session = Depends(get_db)):
    """Validate a discount code."""
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    DiscountService.validate_discount(db_discount, request.order_amount)
    discount_amount = DiscountService.calculate_discount_amount(db_discount, request.order_amount)
    
    return ValidationResponse(valid=True, discount_amount=discount_amount)

@router.put("/{code}", response_model=schemas.Discount)
def update_discount(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    """Update a discount."""
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    update_data = discount_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_discount, key, value)
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
