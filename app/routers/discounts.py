from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])


@router.post("/", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = (
        db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    )
    if db_discount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount code already exists",
        )

    new_discount = models.Discount(**discount.dict())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount


@router.get("/", response_model=List[schemas.Discount])
def list_discounts(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return (
        db.query(models.Discount)
        .filter(models.Discount.is_active, models.Discount.valid_until > now)
        .all()
    )


@router.post("/{code}/validate")
def validate_discount(
    code: str, order_amount: float = Query(0.0), db: Session = Depends(get_db)
):
    discount = DiscountService.get_active_discount(db, code)
    if not discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discount code not found or inactive",
        )

    is_valid, message = DiscountService.validate_discount(discount, order_amount)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    discount_amount = DiscountService.calculate_discount(discount, order_amount)
    return {
        "valid": True,
        "discount_amount": discount_amount,
        "new_total": order_amount - discount_amount,
    }


@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(
    code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)
):
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not discount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Discount code not found"
        )

    if discount_update.is_active is not None:
        discount.is_active = discount_update.is_active

    db.commit()
    db.refresh(discount)
    return discount
