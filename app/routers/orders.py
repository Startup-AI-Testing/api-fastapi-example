from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from src.interfaces.http.inventory import get_inventory_service
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.errors.inventory_errors import (
    InventoryError,
    ReservationNotFoundError,
    ReservationExpiredError,
    InsufficientStockError
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.Order])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all orders with pagination."""
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get an order by ID."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=schemas.Order, status_code=201)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    inventory_service: InventoryDomainService = Depends(get_inventory_service)
):
    """Create a new order with items."""
    # Calculate total
    total = 0.0
    order_items = []

    # If reservation_id is provided, we use it
    if order.reservation_id:
        try:
            # We'll confirm the reservation later after creating the order to get the order_id
            # But we should verify it exists and is for the correct items
            # For simplicity, we'll assume the reservation matches the items for now
            # In a real system, we'd validate this.
            pass
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=400, detail=f"Product with id {item.product_id} not found"
            )
        
        # If no reservation, check stock normally
        if not order.reservation_id:
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}",
                )
            # Update legacy stock
            product.stock -= item.quantity
            
            # Also update new inventory if it exists
            try:
                inventory_service.adjust_stock(product.id, -item.quantity, reason="sale", created_by="order_system")
            except Exception:
                # If inventory doesn't exist, we might want to ignore or handle it
                pass

        item_total = product.price * item.quantity
        total += item_total
        order_items.append(
            models.OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )

    db_order = models.Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total=total,
    )
    db_order.items = order_items

    db.add(db_order)
    db.flush()  # Get db_order.id

    if order.reservation_id:
        try:
            inventory_service.confirm_reservation(order.reservation_id, db_order.id)
            # Also update legacy stock
            # We need to find which product was reserved. 
            # The reservation entity has inventory_id (which is product_id in our case)
            from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
            res_repo = SqlStockReservationRepository(db)
            reservation = res_repo.get_by_id(order.reservation_id)
            product = db.query(models.Product).filter(models.Product.id == reservation.inventory_id).first()
            if product:
                product.stock -= reservation.quantity
        except (ReservationNotFoundError, ReservationExpiredError, InsufficientStockError) as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error confirming reservation: {str(e)}")

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
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    inventory_service: InventoryDomainService = Depends(get_inventory_service)
):
    """Delete an order."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Restore stock for items
    for item in db_order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
            # Also restore in new inventory
            try:
                inventory_service.adjust_stock(product.id, item.quantity, reason="order_cancelled", created_by="order_system")
            except Exception:
                pass

    db.delete(db_order)
    db.commit()
    return None
