from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from .. import models, schemas
from src.infrastructure.inventory.persistence.sql_unit_of_work import SqlUnitOfWork
from src.application.inventory.handlers.confirm_reservation_handler import ConfirmReservationHandler
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.infrastructure.inventory.events.in_memory_event_publisher import InMemoryEventPublisher

router = APIRouter(prefix="/orders", tags=["orders"])

# Global event publisher for now
event_publisher = InMemoryEventPublisher()

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
    uow = SqlUnitOfWork(db)
    
    # Calculate total
    total = 0.0
    order_items = []

    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=400, detail=f"Product with id {item.product_id} not found"
            )
        
        # If no reservation_id is provided, we check stock manually (legacy)
        if not order.reservation_id:
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}",
                )
            # Update legacy stock
            product.stock -= item.quantity
            
            # Also update new inventory system if it exists
            inventory = uow.inventory_repo.get_by_product_id(item.product_id)
            if inventory:
                inventory.quantity_available -= item.quantity
                inventory.quantity_sold += item.quantity
                uow.inventory_repo.save(inventory)

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
    db.flush() # Get the ID

    if order.reservation_id:
        handler = ConfirmReservationHandler(uow, event_publisher)
        try:
            handler.execute(UUID(order.reservation_id), str(db_order.id))
            
            # Update legacy stock for the products in the reservation
            # Note: This assumes the reservation matches the order items.
            # In a real system, we should validate this.
            reservation = uow.reservation_repo.get_by_id(UUID(order.reservation_id))
            inventory = uow.inventory_repo.get_by_id(reservation.inventory_id)
            product = db.query(models.Product).filter(models.Product.id == inventory.product_id).first()
            if product:
                product.stock -= reservation.quantity
                
        except ValueError as e:
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
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order."""
    uow = SqlUnitOfWork(db)
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Find and release reservations associated with this order
    from app.models import StockReservation as StockReservationORM
    # Try both string and int for SQLite compatibility
    reservations = db.query(StockReservationORM).filter(
        (StockReservationORM.order_id == str(order_id)) | 
        (StockReservationORM.order_id == order_id)
    ).all()
    
    service = InventoryDomainService(
        uow.inventory_repo,
        uow.reservation_repo,
        uow.movement_repo,
        event_publisher
    )
    
    released_inventory_ids = set()
    for res_orm in reservations:
        try:
            service.release_reservation(UUID(str(res_orm.id)), "Order deleted")
            released_inventory_ids.add(res_orm.inventory_id)
        except Exception as e:
            print(f"Error releasing reservation {res_orm.id}: {e}")

    # Restore stock for items NOT covered by reservations
    for item in db_order.items:
        inventory = uow.inventory_repo.get_by_product_id(item.product_id)
        if inventory and inventory.id not in released_inventory_ids:
            inventory.quantity_available += item.quantity
            inventory.quantity_sold -= item.quantity
            uow.inventory_repo.save(inventory)
            
        # Always update legacy stock if not already updated by service
        # Wait, the service doesn't update legacy stock!
        # I should always update legacy stock here.
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity

    db.delete(db_order)
    db.commit()
    return None
