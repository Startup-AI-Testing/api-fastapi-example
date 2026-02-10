from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.Order])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.OrderStatus] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all orders with pagination and filters."""
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    if customer_id:
        query = query.filter(models.Order.customer_id == customer_id)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get an order by ID."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=schemas.Order, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with items."""
    # Validate customer
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate total and validate stock
    total = 0.0
    order_items = []

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=400, detail=f"Product with id {item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock}",
            )

        item_total = product.price * item.quantity
        total += item_total
        order_items.append(
            models.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=item_total,
            )
        )
        # Update stock
        product.stock -= item.quantity

    db_order = models.Order(
        customer_id=order.customer_id,
        total=total,
        status=models.OrderStatus.pending,
    )
    db_order.items = order_items

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)
):
    """Update order status with business rules."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status == models.OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot modify a cancelled order")

    new_status = order_update.status
    
    # If cancelling, restore stock
    if new_status == models.OrderStatus.cancelled and db_order.status != models.OrderStatus.cancelled:
        for item in db_order.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity

    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order (only if status is pending)."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if db_order.status != models.OrderStatus.pending:
        raise HTTPException(
            status_code=400, detail="Only pending orders can be deleted"
        )

    # Restore stock for items before deleting
    for item in db_order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    db.delete(db_order)
    db.commit()
    return None
