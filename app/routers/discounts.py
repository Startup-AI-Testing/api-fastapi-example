from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db
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
    
    new_discount = models.Discount(**discount.dict())
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount

@router.get("/", response_model=List[schemas.Discount])
def list_active_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active == True).all()

@router.post("/{code}/validate", response_model=schemas.DiscountValidationResponse)
def validate_discount(code: str, request: schemas.DiscountValidationRequest, db: Session = Depends(get_db)):
    service = DiscountService(db)
    is_valid, amount, message = service.validate_discount(code, request.order_amount)
    return {
        "valid": is_valid,
        "discount_amount": amount,
        "message": message
    }

@router.put("/{code}", response_model=schemas.Discount)
def update_discount(code: str, discount_update: schemas.DiscountUpdate, db: Session = Depends(get_db)):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    if discount_update.is_active is not None:
        db_discount.is_active = discount_update.is_active
    
    db.commit()
    db.refresh(db_discount)
    return db_discount
