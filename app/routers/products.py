from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[schemas.Product])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all products with pagination."""
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@router.get("/search", response_model=List[schemas.Product])
def search_products(
    q: str = None,
    min_price: float = None,
    max_price: float = None,
    in_stock: bool = False,
    db: Session = Depends(get_db),
):
    """Search products by name, price range and stock availability."""
    query = db.query(models.Product)

    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if in_stock:
        query = query.filter(models.Product.stock > 0)

    return query.all()


@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    """Update an existing product."""
    db_product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product."""
    db_product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return None
