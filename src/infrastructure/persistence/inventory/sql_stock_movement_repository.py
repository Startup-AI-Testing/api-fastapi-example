from typing import List
from sqlalchemy.orm import Session
from app.models import StockMovement as StockMovementModel
from src.domain.inventory.entities.stock_movement import StockMovement
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository

class SqlStockMovementRepository(IStockMovementRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, movement: StockMovement) -> None:
        db_movement = StockMovementModel(
            id=movement.id,
            inventory_id=movement.inventory_id,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            reference_id=movement.reference_id,
            created_at=movement.created_at,
            created_by=movement.created_by
        )
        self.session.add(db_movement)
        self.session.commit()

    def get_by_inventory_id(self, inventory_id: int) -> List[StockMovement]:
        db_movements = self.session.query(StockMovementModel).filter_by(
            inventory_id=inventory_id
        ).order_by(StockMovementModel.created_at.desc()).all()
        
        return [
            StockMovement(
                id=db.id,
                inventory_id=db.inventory_id,
                movement_type=db.movement_type,
                quantity=db.quantity,
                reference_id=db.reference_id,
                created_at=db.created_at,
                created_by=db.created_by
            )
            for db in db_movements
        ]
