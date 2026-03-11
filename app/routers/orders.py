from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..database import get_db
from .. import models, schemas

# Inventory imports
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.infrastructure.external.event_publisher import ConsoleEventPublisher as EventPublisher

router = APIRouter(prefix="/orders", tags=["orders"])

def get_inventory_service(db: Session):
    inventory_repo = SqlInventoryRepository(db)
    reservation_repo = SqlStockReservationRepository(db)
    movement_repo = SqlStockMovementRepository(db)
    event_publisher = EventPublisher()
    return InventoryDomainService(inventory_repo, reservation_repo, movement_repo, event_publisher)


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
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order with items."""
    inventory_service = get_inventory_service(db)
    
    # Calculate total and prepare items
    total = 0.0
    order_items = []
    
    # If reservation_ids are provided, we use them
    if order.reservation_ids:
        # Create order first to get ID
        db_order = models.Order(
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total=0.0,  # Will update later
        )
        db.add(db_order)
        db.flush()  # Get ID without committing
        
        # Confirm each reservation
        for res_id in order.reservation_ids:
            try:
                # Convert string to UUID
                res_uuid = uuid.UUID(res_id)
                inventory_service.confirm_reservation(res_uuid, db_order.id)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        # Add items and calculate total
        for item in order.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=400, detail=f"Product with id {item.product_id} not found"
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
            # Update Product.stock to keep it in sync with Inventory.quantity_available
            # Note: Inventory.quantity_available was already decremented during reservation.
            # But Product.stock was not. So we decrement it now.
            product.stock -= item.quantity
            
        db_order.total = total
        db_order.items = order_items
        db.commit()
        db.refresh(db_order)
        return db_order
    else:
        # Old logic (no reservation)
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
            
            # Also update Inventory if it exists
            inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
            if inventory:
                inventory.quantity_available -= item.quantity
                inventory.quantity_sold += item.quantity
                # Record movement
                movement = models.StockMovement(
                    id=str(uuid.uuid4()),
                    inventory_id=inventory.id,
                    movement_type="sale",
                    quantity=-item.quantity,
                    reference_id="direct_order",
                    created_by="system"
                )
                db.add(movement)

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

    inventory_service = get_inventory_service(db)

    # Restore stock for items
    for item in db_order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
        
        # Also update Inventory if it exists
        inventory_service.release_order_stock(order_id, item.product_id, item.quantity)

    db.delete(db_order)
    db.commit()
    return None
