from typing import List
from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository
from src.domain.inventory.entities.stock_movement import StockMovement
from src.infrastructure.persistence.inventory.orm_models import StockMovementORM
from src.infrastructure.persistence.inventory.mappers import StockMovementMapper

class SqlStockMovementRepository(IStockMovementRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, movement: StockMovement) -> None:
        orm = StockMovementMapper.to_orm(movement)
        self.session.add(orm)
        self.session.flush()

    def list_by_inventory_id(self, inventory_id: int) -> List[StockMovement]:
        # This was not in the port but might be useful
        pass
