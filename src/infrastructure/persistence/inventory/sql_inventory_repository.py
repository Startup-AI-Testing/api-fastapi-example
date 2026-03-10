from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.inventory.ports.inventory_ports import IInventoryRepository, IStockReservationRepository, IStockMovementRepository
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainReservation
from src.domain.inventory.entities.stock_movement import StockMovement as DomainMovement
from app.models import Inventory as SqlInventory, StockReservation as SqlReservation, StockMovement as SqlMovement
import uuid
from datetime import datetime

class SqlInventoryRepository(IInventoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, sql_inventory: SqlInventory) -> DomainInventory:
        return DomainInventory(
            product_id=sql_inventory.product_id,
            quantity_available=sql_inventory.quantity_available,
            quantity_reserved=sql_inventory.quantity_reserved,
            quantity_sold=sql_inventory.quantity_sold,
            reorder_point=sql_inventory.reorder_point,
            version=sql_inventory.version,
            last_restocked_at=sql_inventory.last_restocked_at
        )

    def get_by_id(self, inventory_id: int) -> Optional[DomainInventory]:
        sql_inventory = self.db.query(SqlInventory).filter(SqlInventory.id == inventory_id).first()
        return self._to_domain(sql_inventory) if sql_inventory else None

    def get_by_product_id(self, product_id: int) -> Optional[DomainInventory]:
        sql_inventory = self.db.query(SqlInventory).filter(SqlInventory.product_id == product_id).first()
        return self._to_domain(sql_inventory) if sql_inventory else None

    def save(self, inventory: DomainInventory) -> None:
        sql_inventory = self.db.query(SqlInventory).filter(SqlInventory.product_id == inventory.product_id).first()
        if not sql_inventory:
            sql_inventory = SqlInventory(
                product_id=inventory.product_id,
                quantity_available=inventory.quantity_available,
                quantity_reserved=inventory.quantity_reserved,
                quantity_sold=inventory.quantity_sold,
                reorder_point=inventory.reorder_point,
                version=1,
                last_restocked_at=inventory.last_restocked_at
            )
            self.db.add(sql_inventory)
            self.db.flush()
        else:
            # Optimistic locking
            result = self.db.query(SqlInventory).filter(
                SqlInventory.product_id == inventory.product_id,
                SqlInventory.version == inventory.version
            ).update({
                "quantity_available": inventory.quantity_available,
                "quantity_reserved": inventory.quantity_reserved,
                "quantity_sold": inventory.quantity_sold,
                "reorder_point": inventory.reorder_point,
                "version": SqlInventory.version + 1,
                "last_restocked_at": inventory.last_restocked_at
            })
            if result == 0:
                raise Exception("Concurrency conflict: Inventory was modified by another process")
        self.db.commit()

    def get_low_stock(self) -> List[DomainInventory]:
        sql_inventories = self.db.query(SqlInventory).filter(SqlInventory.quantity_available < SqlInventory.reorder_point).all()
        return [self._to_domain(i) for i in sql_inventories]

class SqlStockReservationRepository(IStockReservationRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, sql_res: SqlReservation) -> DomainReservation:
        return DomainReservation(
            id=sql_res.id,
            inventory_id=sql_res.inventory_id,
            quantity=sql_res.quantity,
            reserved_at=sql_res.reserved_at,
            expires_at=sql_res.expires_at,
            status=sql_res.status,
            reservation_type=sql_res.reservation_type,
            order_id=sql_res.order_id
        )

    def get_by_id(self, reservation_id: str) -> Optional[DomainReservation]:
        sql_res = self.db.query(SqlReservation).filter(SqlReservation.id == reservation_id).first()
        if not sql_res:
            # Try with string conversion just in case
            sql_res = self.db.query(SqlReservation).filter(SqlReservation.id == str(reservation_id)).first()
        return self._to_domain(sql_res) if sql_res else None

    def save(self, reservation: DomainReservation) -> None:
        sql_res = self.db.query(SqlReservation).filter(SqlReservation.id == reservation.id).first()
        if not sql_res:
            sql_res = SqlReservation(
                id=reservation.id,
                inventory_id=reservation.inventory_id,
                order_id=reservation.order_id,
                quantity=reservation.quantity,
                reserved_at=reservation.reserved_at,
                expires_at=reservation.expires_at,
                status=reservation.status,
                reservation_type=reservation.reservation_type
            )
            self.db.add(sql_res)
        else:
            sql_res.order_id = reservation.order_id
            sql_res.status = reservation.status
        self.db.commit()

    def get_expired_reservations(self) -> List[DomainReservation]:
        now = datetime.utcnow()
        sql_res = self.db.query(SqlReservation).filter(
            SqlReservation.status == "active",
            SqlReservation.expires_at < now
        ).all()
        return [self._to_domain(r) for r in sql_res]

class SqlStockMovementRepository(IStockMovementRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, movement: DomainMovement) -> None:
        sql_mov = SqlMovement(
            id=str(movement.id),
            inventory_id=movement.inventory_id,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            reference_id=str(movement.reference_id) if movement.reference_id else None,
            created_at=movement.created_at,
            created_by=movement.created_by
        )
        self.db.add(sql_mov)
        self.db.commit()

    def get_by_inventory_id(self, inventory_id: int) -> List[DomainMovement]:
        sql_movs = self.db.query(SqlMovement).filter(SqlMovement.inventory_id == inventory_id).all()
        return [self._to_domain(m) for m in sql_movs]

    def get_all(self) -> List[DomainMovement]:
        sql_movs = self.db.query(SqlMovement).all()
        return [self._to_domain(m) for m in sql_movs]

    def _to_domain(self, m: SqlMovement) -> DomainMovement:
        return DomainMovement(
            id=m.id,
            inventory_id=m.inventory_id,
            movement_type=m.movement_type,
            quantity=m.quantity,
            reference_id=m.reference_id,
            created_at=m.created_at,
            created_by=m.created_by
        )
