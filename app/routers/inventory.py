from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..database import get_db
from .. import schemas
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.domain.inventory.services.inventory_service import InventoryDomainService
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler
from src.application.handlers.inventory.restock_handler import RestockHandler

router = APIRouter(prefix="/inventory", tags=["inventory"])

from src.domain.inventory.ports.inventory_ports import IEventPublisher

class ConsoleEventPublisher(IEventPublisher):
    def publish(self, event):
        print(f"Publishing event: {event}")

def get_inventory_service(db: Session = Depends(get_db)):
    inventory_repo = SqlInventoryRepository(db)
    reservation_repo = SqlStockReservationRepository(db)
    movement_repo = SqlStockMovementRepository(db)
    event_publisher = ConsoleEventPublisher()
    return InventoryDomainService(inventory_repo, reservation_repo, movement_repo, event_publisher)

@router.post("/reserve", response_model=schemas.StockReservation, status_code=status.HTTP_201_CREATED)
def reserve_stock(
    request: schemas.StockReservationCreate,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = ReserveStockHandler(service)
    try:
        return handler.execute(request.product_id, request.quantity, request.reservation_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/reserve/{reservation_id}/confirm")
def confirm_reservation(
    reservation_id: str,
    request: schemas.StockReservationConfirm,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = ConfirmReservationHandler(service)
    try:
        handler.execute(reservation_id, request.order_id)
        return {"message": "Reservation confirmed"}
    except ValueError as e:
        print(f"CONFIRM ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/restock")
def restock(
    request: schemas.RestockRequest,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = RestockHandler(service)
    handler.execute(request.product_id, request.quantity, request.reference)
    return {"message": "Stock restocked successfully"}

@router.post("/adjust")
def adjust_stock(
    request: schemas.StockAdjustment,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    service.adjust_stock(request.product_id, request.quantity, request.reason)
    return {"message": "Stock adjusted successfully"}

@router.get("/movements", response_model=List[schemas.StockMovement])
def get_movements(
    product_id: Optional[int] = None,
    service: InventoryDomainService = Depends(get_inventory_service)
):
    if product_id:
        return service.movement_repo.get_by_inventory_id(product_id)
    return service.movement_repo.get_all()

@router.get("/low-stock", response_model=List[schemas.Inventory])
def get_low_stock(
    service: InventoryDomainService = Depends(get_inventory_service)
):
    return service.inventory_repo.get_low_stock()
