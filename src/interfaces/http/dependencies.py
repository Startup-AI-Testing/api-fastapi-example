from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.domain.inventory.services.inventory_service import InventoryDomainService
from src.application.handlers.inventory.reserve_stock_handler import ReserveStockHandler
from src.application.handlers.inventory.confirm_reservation_handler import ConfirmReservationHandler
from src.application.handlers.inventory.restock_handler import RestockHandler

def get_inventory_repo(db: Session = Depends(get_db)):
    return SqlInventoryRepository(db)

def get_reservation_repo(db: Session = Depends(get_db)):
    return SqlStockReservationRepository(db)

def get_movement_repo(db: Session = Depends(get_db)):
    return SqlStockMovementRepository(db)

def get_inventory_service(
    inventory_repo=Depends(get_inventory_repo),
    reservation_repo=Depends(get_reservation_repo),
    movement_repo=Depends(get_movement_repo)
):
    return InventoryDomainService(inventory_repo, reservation_repo, movement_repo)

def get_reserve_stock_handler(service=Depends(get_inventory_service)):
    return ReserveStockHandler(service)

def get_confirm_reservation_handler(service=Depends(get_inventory_service)):
    return ConfirmReservationHandler(service)

def get_restock_handler(service=Depends(get_inventory_service)):
    return RestockHandler(service)
