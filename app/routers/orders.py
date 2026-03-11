from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.Order])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all orders with pagination."""
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders


@router.get("/stats", response_model=schemas.OrderStats)
def get_order_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """Get order statistics with optional date filtering."""
    query = db.query(models.Order)

    if date_from:
        dt_from = datetime.combine(date_from, datetime.min.time())
        query = query.filter(models.Order.created_at >= dt_from)
    if date_to:
        dt_to = datetime.combine(date_to, datetime.max.time())
        query = query.filter(models.Order.created_at <= dt_to)

    stats = query.with_entities(
        func.count(models.Order.id).label("total_orders"),
        func.sum(models.Order.total).label("total_revenue"),
        func.avg(models.Order.total).label("average_order_value"),
    ).first()

    total_orders = stats.total_orders or 0
    total_revenue = stats.total_revenue or 0.0
    average_order_value = stats.average_order_value or 0.0

    # Top product
    top_product_query = (
        db.query(
            models.OrderItem.product_id,
            func.sum(models.OrderItem.quantity).label("total_quantity"),
        )
        .join(models.Order)
        .group_by(models.OrderItem.product_id)
        .order_by(func.sum(models.OrderItem.quantity).desc())
    )

    if date_from:
        dt_from = datetime.combine(date_from, datetime.min.time())
        top_product_query = top_product_query.filter(models.Order.created_at >= dt_from)
    if date_to:
        dt_to = datetime.combine(date_to, datetime.max.time())
        top_product_query = top_product_query.filter(models.Order.created_at <= dt_to)

    top_product = top_product_query.first()
    top_product_id = top_product.product_id if top_product else None

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_order_value": average_order_value,
        "top_product_id": top_product_id,
    }


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
    # Calculate total
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
            )
        )
        # Update stock
        product.stock -= item.quantity

    db_order = models.Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total=total,
    )
    db_order.items = order_items

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)
):
    """Update an existing order (customer info and status only)."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Restore stock for items
    for item in db_order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    db.delete(db_order)
    db.commit()
    return None
