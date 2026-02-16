from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("/", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = models.Discount(
        code=discount.code.upper(),
        discount_type=discount.discount_type,
        discount_value=discount.discount_value,
        min_order_amount=discount.min_order_amount,
        max_uses=discount.max_uses,
        valid_from=discount.valid_from,
        valid_until=discount.valid_until,
        is_active=discount.is_active
    )
    db.add(db_discount)
    try:
        db.commit()
        db.refresh(db_discount)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Discount code already exists")
    return db_discount

@router.get("/", response_model=List[schemas.Discount])
def list_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active).all()

@router.post("/{code}/validate", response_model=schemas.Discount)
def validate_discount(code: str, order_amount: float, db: Session = Depends(get_db)):
    discount = DiscountService.validate_discount(db, code, order_amount)
    if not discount:
        raise HTTPException(status_code=400, detail="Invalid or expired discount code")
    return discount

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    discount = db.query(models.Discount).filter(models.Discount.code == code.upper()).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    discount.is_active = discount_update.is_active
    db.commit()
    db.refresh(discount)
    return discount
