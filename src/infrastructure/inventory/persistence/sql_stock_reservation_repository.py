from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainStockReservation
from app.models import StockReservation as SqlStockReservation
from datetime import datetime

class SqlStockReservationRepository(IStockReservationRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, reservation_id: UUID) -> Optional[DomainStockReservation]:
        sql_res = self.session.query(SqlStockReservation).filter_by(id=str(reservation_id)).first()
        if not sql_res:
            return None
        return self._to_domain(sql_res)

    def save(self, reservation: DomainStockReservation) -> None:
        sql_res = self.session.query(SqlStockReservation).filter_by(id=str(reservation.id)).first()
        if sql_res:
            sql_res.order_id = str(reservation.order_id) if reservation.order_id else None
            sql_res.status = reservation.status
            sql_res.expires_at = reservation.expires_at
        else:
            sql_res = SqlStockReservation(
                id=str(reservation.id),
                inventory_id=reservation.inventory_id,
                order_id=str(reservation.order_id) if reservation.order_id else None,
                quantity=reservation.quantity,
                reserved_at=reservation.reserved_at,
                expires_at=reservation.expires_at,
                status=reservation.status,
                reservation_type=reservation.reservation_type
            )
            self.session.add(sql_res)

    def list_expired(self) -> List[DomainStockReservation]:
        now = datetime.utcnow()
        sql_reservations = self.session.query(SqlStockReservation).filter(
            SqlStockReservation.status == "active",
            SqlStockReservation.expires_at < now
        ).all()
        return [self._to_domain(r) for r in sql_reservations]

    def _to_domain(self, sql_res: SqlStockReservation) -> DomainStockReservation:
        return DomainStockReservation(
            id=UUID(sql_res.id),
            inventory_id=sql_res.inventory_id,
            order_id=sql_res.order_id,
            quantity=sql_res.quantity,
            reserved_at=sql_res.reserved_at,
            expires_at=sql_res.expires_at,
            status=sql_res.status,
            reservation_type=sql_res.reservation_type
        )
