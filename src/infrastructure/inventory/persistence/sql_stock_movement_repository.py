from typing import List
from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository
from src.domain.inventory.entities.stock_movement import StockMovement as DomainStockMovement
from app.models import StockMovement as SqlStockMovement
from uuid import UUID

class SqlStockMovementRepository(IStockMovementRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, movement: DomainStockMovement) -> None:
        sql_mov = SqlStockMovement(
            id=str(movement.id),
            inventory_id=movement.inventory_id,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            reference_id=str(movement.reference_id) if movement.reference_id else None,
            created_at=movement.created_at,
            created_by=movement.created_by
        )
        self.session.add(sql_mov)

    def get_by_inventory_id(self, inventory_id: int) -> List[DomainStockMovement]:
        sql_movements = self.session.query(SqlStockMovement).filter_by(inventory_id=inventory_id).all()
        return [self._to_domain(m) for m in sql_movements]

    def _to_domain(self, sql_mov: SqlStockMovement) -> DomainStockMovement:
        return DomainStockMovement(
            id=UUID(sql_mov.id),
            inventory_id=sql_mov.inventory_id,
            movement_type=sql_mov.movement_type,
            quantity=sql_mov.quantity,
            reference_id=UUID(sql_mov.reference_id) if sql_mov.reference_id else None,
            created_at=sql_mov.created_at,
            created_by=sql_mov.created_by
        )
