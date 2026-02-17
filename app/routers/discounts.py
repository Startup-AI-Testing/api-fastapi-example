from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import schemas, models
from ..services.discount_service import DiscountService

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"]
)

@router.post("/", response_model=schemas.Discount)
def create_discount(discount: schemas.DiscountCreate, db: Session = Depends(get_db)):
    db_discount = models.Discount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("/", response_model=List[schemas.Discount])
def list_discounts(db: Session = Depends(get_db)):
    return db.query(models.Discount).filter(models.Discount.is_active.is_(True)).all()

@router.post("/{code}/validate", response_model=schemas.DiscountValidationResponse)
def validate_discount(
    code: str, 
    validation_request: schemas.DiscountValidationRequest, 
    db: Session = Depends(get_db)
):
    service = DiscountService(db)
    is_valid, message, discount = service.validate_discount(code, validation_request.order_amount)
    return {"is_valid": is_valid, "message": message, "discount": discount}

@router.put("/{code}", response_model=schemas.Discount)
def update_discount_status(
    code: str, 
    status_update: schemas.DiscountStatusUpdate, 
    db: Session = Depends(get_db)
):
    db_discount = db.query(models.Discount).filter(models.Discount.code == code).first()
    if not db_discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    
    db_discount.is_active = status_update.is_active
    db.commit()
    db.refresh(db_discount)
    return db_discount
