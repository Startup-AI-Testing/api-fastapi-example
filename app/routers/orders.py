from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from .. import models, schemas
from src.interfaces.http.dependencies import get_confirm_reservation_handler, get_inventory_service
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler
from src.domain.inventory.services.inventory_service import InventoryDomainService

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
    confirm_handler: ConfirmReservationHandler = Depends(get_confirm_reservation_handler)
):
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
        
        # If no reservation, check stock directly
        if not order.reservation_id:
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}",
                )
            # Update legacy stock
            product.stock -= item.quantity
            
            # Also update new inventory if exists
            inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
            if inventory:
                if inventory.quantity_available < item.quantity:
                     raise HTTPException(status_code=400, detail="Insufficient inventory available")
                inventory.quantity_available -= item.quantity
                inventory.quantity_sold += item.quantity

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
        reservation_id=order.reservation_id
    )
    db_order.items = order_items

    db.add(db_order)
    db.flush()

    if order.reservation_id:
        try:
            confirm_handler.execute(order.reservation_id, str(db_order.id))
            
            # Update legacy stock for the reserved item
            reservation = db.query(models.StockReservation).filter(models.StockReservation.id == order.reservation_id).first()
            if reservation:
                product = db.query(models.Product).filter(models.Product.id == reservation.inventory_id).first()
                if product:
                    product.stock -= reservation.quantity
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

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

    # If it has a reservation, release it
    if db_order.reservation_id:
        try:
            inventory_service.release_reservation(db_order.reservation_id, reason=f"Order {order_id} deleted")
        except Exception:
            pass

    # Restore stock for items
    for item in db_order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
            
        if not db_order.reservation_id:
            inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
            if inventory:
                inventory.quantity_sold -= item.quantity
                inventory.quantity_available += item.quantity

    db.delete(db_order)
    db.commit()
    return None
