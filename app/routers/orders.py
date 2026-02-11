from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with items, validating stock."""
    # Validate customer
    db_customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db_order = models.Order(
        customer_id=order.customer_id,
        status=schemas.OrderStatus.pending,
        total=0.0
    )
    db.add(db_order)
    db.flush()  # Get db_order.id

    total = 0.0
    for item in order.items:
        db_product = db.query(models.Product).filter(models.Product.id == item.product_id).with_for_update().first()
        if not db_product:
            db.rollback()
            raise HTTPException(
                status_code=400, detail=f"Product with id {item.product_id} not found"
            )
        
        if db_product.stock < item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {db_product.name}. Available: {db_product.stock}",
            )

        subtotal = db_product.price * item.quantity
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=db_product.price,
            subtotal=subtotal
        )
        
        # Update stock
        db_product.stock -= item.quantity
        total += subtotal
        db.add(order_item)

    db_order.total = total
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[schemas.Order])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.OrderStatus] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all orders with pagination and filters."""
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    if customer_id:
        query = query.filter(models.Order.customer_id == customer_id)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get an order by ID with its items."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int, 
    status_update: schemas.OrderUpdate, 
    db: Session = Depends(get_db)
):
    """Update order status. Restores stock if cancelled."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).with_for_update().first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status == schemas.OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot modify a cancelled order")

    new_status = status_update.status
    if not new_status:
         raise HTTPException(status_code=400, detail="Status is required")

    # If cancelling, restore stock
    if new_status == schemas.OrderStatus.cancelled and db_order.status != schemas.OrderStatus.cancelled:
        for item in db_order.items:
            db_product = db.query(models.Product).filter(models.Product.id == item.product_id).with_for_update().first()
            if db_product:
                db_product.stock += item.quantity

    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete a pending order and restore stock."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != schemas.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be deleted")

    # Restore stock
    for item in db_order.items:
        db_product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if db_product:
            db_product.stock += item.quantity

    db.delete(db_order)
    db.commit()
    return None
