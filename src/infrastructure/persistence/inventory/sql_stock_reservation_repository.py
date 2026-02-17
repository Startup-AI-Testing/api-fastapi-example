from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import StockReservation as StockReservationModel
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository

class SqlStockReservationRepository(IStockReservationRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, reservation_id: UUID) -> Optional[StockReservation]:
        db_res = self.session.query(StockReservationModel).filter_by(id=reservation_id).first()
        if not db_res:
            return None
        
        return StockReservation(
            id=db_res.id,
            inventory_id=db_res.inventory_id,
            order_id=db_res.order_id,
            quantity=db_res.quantity,
            reserved_at=db_res.reserved_at,
            expires_at=db_res.expires_at,
            status=db_res.status,
            reservation_type=db_res.reservation_type
        )

    def save(self, reservation: StockReservation) -> None:
        db_res = self.session.query(StockReservationModel).filter_by(id=reservation.id).first()
        
        if not db_res:
            db_res = StockReservationModel(
                id=reservation.id,
                inventory_id=reservation.inventory_id,
                order_id=reservation.order_id,
                quantity=reservation.quantity,
                reserved_at=reservation.reserved_at,
                expires_at=reservation.expires_at,
                status=reservation.status,
                reservation_type=reservation.reservation_type
            )
            self.session.add(db_res)
        else:
            db_res.order_id = reservation.order_id
            db_res.status = reservation.status
            db_res.expires_at = reservation.expires_at
            
        self.session.commit()

    def get_expired_reservations(self) -> List[StockReservation]:
        current_time = datetime.utcnow()
        db_expired = self.session.query(StockReservationModel).filter(
            StockReservationModel.status == "active",
            StockReservationModel.expires_at <= current_time
        ).all()
        
        return [
            StockReservation(
                id=db.id,
                inventory_id=db.inventory_id,
                order_id=db.order_id,
                quantity=db.quantity,
                reserved_at=db.reserved_at,
                expires_at=db.expires_at,
                status=db.status,
                reservation_type=db.reservation_type
            )
            for db in db_expired
        ]
