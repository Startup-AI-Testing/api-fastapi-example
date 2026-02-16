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

@router.post("/", response_model=schemas.Discount, status_code=status.HTTP_201_CREATED)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if db_discount:
        raise HTTPException(status_code=400, detail="Discount code already exists")
    
    new_discount = models.Discount(**discount.model_dump())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("/", response_model=List[schemas.Discount])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active.is_(True)).all()

@router.post("/{code}/validate", response_model=schemas.DiscountValidateResponse)
def validate_discount(
    code: str, 
    request: schemas.DiscountValidateRequest, 
    db: Session = Depends(get_db)
):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        return {"valid": False, "discount": None, "error": "Discount code not found"}
    
    valid, error = DiscountService.validate_discount(db_discount, float(request.order_amount))
    return {"valid": valid, "discount": db_discount if valid else None, "error": error}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount(
    code: str, 
    discount_update: schemas.DiscountUpdate, 
    db: Session = Depends(get_db)
):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    if discount_update.is_active is not None:
        db_discount.is_active = discount_update.is_active
        db.commit()
        db.refresh(db_discount)
    
    return db_discount
