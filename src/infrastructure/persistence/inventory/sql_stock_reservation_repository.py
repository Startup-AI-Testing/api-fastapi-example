from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.infrastructure.persistence.inventory.orm_models import StockReservationORM
from src.infrastructure.persistence.inventory.mappers import StockReservationMapper
import uuid
from datetime import datetime

class SqlStockReservationRepository(IStockReservationRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, reservation_id: uuid.UUID) -> Optional[StockReservation]:
        orm = self.session.query(StockReservationORM).get(str(reservation_id))
        if not orm:
            return None
        return StockReservationMapper.to_domain(orm)

    def save(self, reservation: StockReservation) -> None:
        orm = self.session.query(StockReservationORM).get(str(reservation.id))
        if orm:
            orm.status = reservation.status
            orm.order_id = reservation.order_id
        else:
            orm = StockReservationMapper.to_orm(reservation)
            self.session.add(orm)
        self.session.flush()

    def list_expired(self) -> List[StockReservation]:
        now = datetime.utcnow()
        orms = self.session.query(StockReservationORM).filter(
            StockReservationORM.status == "active",
            StockReservationORM.expires_at < now
        ).all()
        return [StockReservationMapper.to_domain(orm) for orm in orms]
