from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.infrastructure.persistence.inventory.orm_models import InventoryORM, StockReservationORM, StockMovementORM
import uuid

class InventoryMapper:
    @staticmethod
    def to_domain(orm: InventoryORM) -> Inventory:
        return Inventory(
            product_id=orm.product_id,
            quantity_available=orm.quantity_available,
            quantity_reserved=orm.quantity_reserved,
            quantity_sold=orm.quantity_sold,
            reorder_point=orm.reorder_point,
            version=orm.version,
            last_restocked_at=orm.last_restocked_at
        )

    @staticmethod
    def to_orm(domain: Inventory) -> InventoryORM:
        return InventoryORM(
            product_id=domain.product_id,
            quantity_available=domain.quantity_available,
            quantity_reserved=domain.quantity_reserved,
            quantity_sold=domain.quantity_sold,
            reorder_point=domain.reorder_point,
            version=domain.version,
            last_restocked_at=domain.last_restocked_at
        )

class StockReservationMapper:
    @staticmethod
    def to_domain(orm: StockReservationORM) -> StockReservation:
        return StockReservation(
            id=uuid.UUID(str(orm.id)),
            inventory_id=orm.inventory_id,
            order_id=orm.order_id,
            quantity=orm.quantity,
            reserved_at=orm.reserved_at,
            expires_at=orm.expires_at,
            status=orm.status,
            reservation_type=orm.reservation_type
        )

    @staticmethod
    def to_orm(domain: StockReservation) -> StockReservationORM:
        return StockReservationORM(
            id=str(domain.id),
            inventory_id=domain.inventory_id,
            order_id=domain.order_id,
            quantity=domain.quantity,
            reserved_at=domain.reserved_at,
            expires_at=domain.expires_at,
            status=domain.status,
            reservation_type=domain.reservation_type
        )

class StockMovementMapper:
    @staticmethod
    def to_orm(domain: StockMovement) -> StockMovementORM:
        return StockMovementORM(
            id=str(domain.id),
            inventory_id=domain.inventory_id,
            movement_type=domain.movement_type,
            quantity=domain.quantity,
            reference_id=str(domain.reference_id) if domain.reference_id else None,
            created_at=domain.created_at,
            created_by=domain.created_by
        )
