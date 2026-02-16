from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository
from src.infrastructure.inventory.persistence.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.inventory.persistence.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.inventory.persistence.sql_stock_movement_repository import SqlStockMovementRepository

class SqlUnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self.inventory_repo = SqlInventoryRepository(session)
        self.reservation_repo = SqlStockReservationRepository(session)
        self.movement_repo = SqlStockMovementRepository(session)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
