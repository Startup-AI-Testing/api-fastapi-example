from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.discount_service import DiscountService

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"],
)

@router.post("", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount code already exists"
        )
    
    new_discount = models.Discount(**discount.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("", response_model=List[schemas.Discount])
def get_active_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active).all()

@router.post("/{code}/validate", response_model=schemas.Discount)
def validate_discount(code: str, order_amount: float, db: Session = Depends(get_db)):
    return DiscountService.validate_discount(db, code, order_amount)

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount not found"
        )
    
    if discount_update.is_active is not None:
        db_discount.is_active = discount_update.is_active
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
