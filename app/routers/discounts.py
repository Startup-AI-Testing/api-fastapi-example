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
def list_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active).all()

@router.post("/{code}/validate")
def validate_discount(code: str, order_amount: float, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    DiscountService.validate_discount(discount, order_amount)
    return {"valid": True, "discount_amount": DiscountService.calculate_discount(discount, order_amount)}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount code not found")
    
    update_data = discount_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_discount, key, value)
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
