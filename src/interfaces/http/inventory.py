from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from src.interfaces.http.schemas.inventory_schemas import (
    ReserveStockRequest, ConfirmReservationRequest, RestockRequest,
    AdjustStockRequest, InventoryResponse, ReservationResponse,
    StockMovementResponse
)
from src.infrastructure.inventory.persistence.sql_unit_of_work import SqlUnitOfWork
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.application.inventory.handlers.reserve_stock_handler import ReserveStockHandler
from src.application.inventory.handlers.confirm_reservation_handler import ConfirmReservationHandler
from src.application.inventory.handlers.restock_handler import RestockHandler

router = APIRouter(prefix="/inventory", tags=["inventory"])

from src.infrastructure.inventory.events.in_memory_event_publisher import InMemoryEventPublisher

# Global event publisher for now
event_publisher = InMemoryEventPublisher()

def get_inventory_service(db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    return InventoryDomainService(
        uow.inventory_repo,
        uow.reservation_repo,
        uow.movement_repo,
        event_publisher
    )

@router.post("/reserve", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def reserve_stock(request: ReserveStockRequest, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    handler = ReserveStockHandler(uow, event_publisher)
    try:
        return handler.execute(request.product_id, request.quantity, request.reservation_type)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/reserve/{reservation_id}/confirm", response_model=ReservationResponse)
def confirm_reservation(reservation_id: UUID, request: ConfirmReservationRequest, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    handler = ConfirmReservationHandler(uow, event_publisher)
    try:
        res = handler.execute(reservation_id, request.order_id)
        if res is None:
             raise ValueError("Reservation not found after confirmation")
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in endpoint: {e}")
        raise

@router.delete("/reserve/{reservation_id}")
def release_reservation(reservation_id: UUID, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    service = get_inventory_service(db)
    try:
        with uow:
            service.release_reservation(reservation_id, "Manual release")
            uow.commit()
            return {"status": "released", "reservation_id": str(reservation_id)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_availability(product_id: int, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    inv = uow.inventory_repo.get_by_product_id(product_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inv

@router.post("/restock", response_model=InventoryResponse)
def restock(request: RestockRequest, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    handler = RestockHandler(uow, event_publisher)
    try:
        handler.execute(request.product_id, request.quantity, request.created_by)
        return uow.inventory_repo.get_by_product_id(request.product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/adjust", response_model=InventoryResponse)
def adjust_stock(request: AdjustStockRequest, db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    service = get_inventory_service(db)
    try:
        with uow:
            inv = service.adjust_stock(request.product_id, request.quantity, request.reason, request.created_by)
            uow.commit()
            return inv
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/movements", response_model=List[StockMovementResponse])
def get_movements(db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    # This is a bit hacky as we don't have a specific method for all movements in repo yet
    from app.models import StockMovement
    movements = db.query(StockMovement).all()
    return movements

@router.get("/low-stock", response_model=List[InventoryResponse])
def get_low_stock(db: Session = Depends(get_db)):
    uow = SqlUnitOfWork(db)
    # Again, hacky
    from app.models import Inventory
    low_stock = db.query(Inventory).filter(Inventory.quantity_available < Inventory.reorder_point).all()
    return low_stock
