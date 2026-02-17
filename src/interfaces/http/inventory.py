from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas

from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.persistence.inventory.sql_stock_movement_repository import SqlStockMovementRepository
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler, ReserveStockCommand
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler, ConfirmReservationCommand
from src.application.handlers.inventory.restock_handler import RestockHandler, RestockCommand
from src.domain.inventory.errors.inventory_errors import (
    InsufficientStockError,
    InventoryNotFoundError,
    ReservationNotFoundError,
    ReservationExpiredError,
    ConcurrencyError
)

from src.infrastructure.external.event_publisher import InMemoryEventPublisher

from uuid import UUID

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Global event publisher for now, or we could inject it
event_publisher = InMemoryEventPublisher()

def get_inventory_service(db: Session = Depends(get_db)):
    inventory_repo = SqlInventoryRepository(db)
    reservation_repo = SqlStockReservationRepository(db)
    movement_repo = SqlStockMovementRepository(db)
    return InventoryDomainService(inventory_repo, reservation_repo, movement_repo, event_publisher)

@router.post("/reserve", response_model=schemas.StockReservation, status_code=status.HTTP_201_CREATED)
def reserve_stock(
    request: schemas.StockReservationCreate,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = ReserveStockHandler(service)
    try:
        command = ReserveStockCommand(
            product_id=request.product_id,
            quantity=request.quantity,
            reservation_type=request.reservation_type
        )
        return handler.execute(command)
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InventoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConcurrencyError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/reserve/{reservation_id}/confirm", response_model=schemas.StockReservation)
def confirm_reservation(
    reservation_id: UUID,
    request: schemas.StockReservationConfirm,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = ConfirmReservationHandler(service)
    try:
        command = ConfirmReservationCommand(
            reservation_id=reservation_id,
            order_id=request.order_id
        )
        return handler.execute(command)
    except (ReservationNotFoundError, InventoryNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ReservationExpiredError, ConcurrencyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/reserve/{reservation_id}")
def release_reservation(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    try:
        service.release_reservation(reservation_id)
        return {"status": "released"}
    except ReservationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConcurrencyError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/product/{product_id}", response_model=schemas.Inventory)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    inventory = service.inventory_repo.get_by_product_id(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.post("/restock", response_model=schemas.Inventory)
def restock(
    request: schemas.RestockRequest,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    handler = RestockHandler(service)
    try:
        command = RestockCommand(
            product_id=request.product_id,
            quantity=request.quantity
        )
        return handler.execute(command)
    except InventoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConcurrencyError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/adjust", response_model=schemas.Inventory)
def adjust_stock(
    request: schemas.StockAdjustmentRequest,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    try:
        return service.adjust_stock(
            product_id=request.product_id,
            quantity=request.quantity,
            reason=request.reason
        )
    except InventoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConcurrencyError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/movements", response_model=List[schemas.StockMovement])
def get_movements(
    product_id: int = None,
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    if product_id:
        inventory = service.inventory_repo.find_by_product_id(product_id)
        if not inventory:
            return []
        return service.movement_repo.find_by_inventory_id(inventory.id)
    # This might need a better implementation in repo if we want all movements
    return []

@router.get("/low-stock", response_model=List[schemas.Inventory])
def get_low_stock(
    db: Session = Depends(get_db),
    service: InventoryDomainService = Depends(get_inventory_service)
):
    return service.inventory_repo.find_low_stock()
