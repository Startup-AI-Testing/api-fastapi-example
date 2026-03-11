from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.infrastructure.external.event_publisher import ConsoleEventPublisher
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler
from src.application.handlers.inventory.release_reservation_handler import ReleaseReservationHandler
from src.application.handlers.inventory.restock_handler import RestockHandler
from src.application.handlers.inventory.adjust_stock_handler import AdjustStockHandler
from src.interfaces.http.schemas import (
    ReserveStockRequest, 
    ConfirmReservationRequest, 
    RestockRequest, 
    AdjustStockRequest,
    InventoryResponse,
    ReservationResponse,
    MovementResponse
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

def get_inventory_service(db: Session = Depends(get_db)) -> InventoryDomainService:
    inventory_repo = SqlInventoryRepository(db)
    reservation_repo = SqlStockReservationRepository(db)
    movement_repo = SqlStockMovementRepository(db)
    event_publisher = ConsoleEventPublisher()
    return InventoryDomainService(
        inventory_repo=inventory_repo,
        reservation_repo=reservation_repo,
        movement_repo=movement_repo,
        event_publisher=event_publisher
    )

@router.post("/reserve", response_model=ReservationResponse)
def reserve_stock(
    request: ReserveStockRequest, 
    service: InventoryDomainService = Depends(get_inventory_service),
    db: Session = Depends(get_db)
):
    try:
        handler = ReserveStockHandler(service)
        result = handler.execute(
            product_id=request.product_id,
            quantity=request.quantity,
            reservation_type=request.reservation_type
        )
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/reserve/{id}/confirm")
def confirm_reservation(
    id: UUID, 
    request: ConfirmReservationRequest, 
    service: InventoryDomainService = Depends(get_inventory_service),
    db: Session = Depends(get_db)
):
    try:
        handler = ConfirmReservationHandler(service)
        handler.execute(reservation_id=id, order_id=request.order_id)
        db.commit()
        return {"message": "Reservation confirmed"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/reserve/{id}")
def release_reservation(
    id: UUID, 
    service: InventoryDomainService = Depends(get_inventory_service),
    db: Session = Depends(get_db)
):
    try:
        handler = ReleaseReservationHandler(service)
        handler.execute(reservation_id=id)
        db.commit()
        return {"message": "Reservation released"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/product/{id}", response_model=InventoryResponse)
def get_product_inventory(
    id: int, 
    service: InventoryDomainService = Depends(get_inventory_service)
):
    inventory = service.inventory_repo.get_by_product_id(id)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory

@router.post("/restock")
def restock(
    request: RestockRequest, 
    service: InventoryDomainService = Depends(get_inventory_service),
    db: Session = Depends(get_db)
):
    try:
        handler = RestockHandler(service)
        handler.execute(
            product_id=request.product_id,
            quantity=request.quantity,
            reference=request.reference
        )
        db.commit()
        return {"message": "Stock restocked"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/adjust")
def adjust_stock(
    data: AdjustStockRequest, 
    service: InventoryDomainService = Depends(get_inventory_service),
    db: Session = Depends(get_db)
):
    try:
        handler = AdjustStockHandler(service)
        handler.execute(
            product_id=data.product_id,
            quantity=data.quantity,
            reason=data.reason
        )
        db.commit()
        return {"message": "Stock adjusted"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/movements", response_model=List[MovementResponse])
def get_movements(service: InventoryDomainService = Depends(get_inventory_service)):
    return service.movement_repo.list_all()

@router.get("/low-stock", response_model=List[InventoryResponse])
def get_low_stock(service: InventoryDomainService = Depends(get_inventory_service)):
    return service.inventory_repo.get_low_stock()
