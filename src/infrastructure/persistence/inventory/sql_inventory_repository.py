from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from src.domain.inventory.entities.stock_reservation import StockReservation as DomainReservation
from src.domain.inventory.entities.stock_movement import StockMovement as DomainMovement
from src.domain.inventory.ports.repository_ports import (
    IInventoryRepository, 
    IStockReservationRepository, 
    IStockMovementRepository
)
from app import models
from datetime import datetime

class SqlInventoryRepository(IInventoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_product_id(self, product_id: int) -> Optional[DomainInventory]:
        db_inventory = self.db.query(models.Inventory).filter(
            models.Inventory.product_id == product_id
        ).first()
        
        if not db_inventory:
            return None
        
        return DomainInventory(
            product_id=db_inventory.product_id,
            quantity_available=db_inventory.quantity_available,
            quantity_reserved=db_inventory.quantity_reserved,
            quantity_sold=db_inventory.quantity_sold,
            reorder_point=db_inventory.reorder_point,
            version=db_inventory.version,
            last_restocked_at=db_inventory.last_restocked_at
        )

    def save(self, inventory: DomainInventory) -> None:
        db_inventory = self.db.query(models.Inventory).filter(
            models.Inventory.product_id == inventory.product_id
        ).first()
        
        if not db_inventory:
            db_inventory = models.Inventory(
                product_id=inventory.product_id,
                quantity_available=inventory.quantity_available,
                quantity_reserved=inventory.quantity_reserved,
                quantity_sold=inventory.quantity_sold,
                reorder_point=inventory.reorder_point,
                version=inventory.version,
                last_restocked_at=inventory.last_restocked_at
            )
            self.db.add(db_inventory)
        else:
            # Optimistic locking
            if db_inventory.version != inventory.version:
                raise Exception("Concurrency conflict: Inventory version mismatch")
            
            db_inventory.quantity_available = inventory.quantity_available
            db_inventory.quantity_reserved = inventory.quantity_reserved
            db_inventory.quantity_sold = inventory.quantity_sold
            db_inventory.reorder_point = inventory.reorder_point
            db_inventory.last_restocked_at = inventory.last_restocked_at
            db_inventory.version += 1
            inventory.version = db_inventory.version # Update domain entity version

    def get_low_stock(self) -> List[DomainInventory]:
        db_inventories = self.db.query(models.Inventory).filter(
            models.Inventory.quantity_available < models.Inventory.reorder_point
        ).all()
        
        return [
            DomainInventory(
                product_id=i.product_id,
                quantity_available=i.quantity_available,
                quantity_reserved=i.quantity_reserved,
                quantity_sold=i.quantity_sold,
                reorder_point=i.reorder_point,
                version=i.version,
                last_restocked_at=i.last_restocked_at
            ) for i in db_inventories
        ]

class SqlStockReservationRepository(IStockReservationRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reservation_id: UUID) -> Optional[DomainReservation]:
        db_res = self.db.query(models.StockReservation).filter(
            models.StockReservation.id == reservation_id
        ).first()
        
        if not db_res:
            return None
        
        return DomainReservation(
            id=db_res.id,
            inventory_id=db_res.inventory_id,
            quantity=db_res.quantity,
            reserved_at=db_res.reserved_at,
            expires_at=db_res.expires_at,
            status=db_res.status,
            reservation_type=db_res.reservation_type,
            order_id=db_res.order_id
        )

    def save(self, reservation: DomainReservation) -> None:
        db_res = self.db.query(models.StockReservation).filter(
            models.StockReservation.id == reservation.id
        ).first()
        
        if not db_res:
            db_res = models.StockReservation(
                id=reservation.id,
                inventory_id=reservation.inventory_id,
                quantity=reservation.quantity,
                reserved_at=reservation.reserved_at,
                expires_at=reservation.expires_at,
                status=reservation.status,
                reservation_type=reservation.reservation_type,
                order_id=reservation.order_id
            )
            self.db.add(db_res)
        else:
            db_res.status = reservation.status
            db_res.order_id = reservation.order_id

    def get_expired_reservations(self) -> List[DomainReservation]:
        now = datetime.utcnow()
        db_res = self.db.query(models.StockReservation).filter(
            models.StockReservation.status == "active",
            models.StockReservation.expires_at < now
        ).all()
        
        return [
            DomainReservation(
                id=r.id,
                inventory_id=r.inventory_id,
                quantity=r.quantity,
                reserved_at=r.reserved_at,
                expires_at=r.expires_at,
                status=r.status,
                reservation_type=r.reservation_type,
                order_id=r.order_id
            ) for r in db_res
        ]

class SqlStockMovementRepository(IStockMovementRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, movement: DomainMovement) -> None:
        db_movement = models.StockMovement(
            id=movement.id,
            inventory_id=movement.inventory_id,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            reference_id=movement.reference_id,
            created_at=movement.created_at,
            created_by=movement.created_by
        )
        self.db.add(db_movement)

    def get_by_inventory_id(self, inventory_id: int) -> List[DomainMovement]:
        db_movements = self.db.query(models.StockMovement).filter(
            models.StockMovement.inventory_id == inventory_id
        ).all()
        
        return [
            DomainMovement(
                id=m.id,
                inventory_id=m.inventory_id,
                movement_type=m.movement_type,
                quantity=m.quantity,
                reference_id=m.reference_id,
                created_at=m.created_at,
                created_by=m.created_by
            ) for m in db_movements
        ]

    def list_all(self) -> List[DomainMovement]:
        db_movements = self.db.query(models.StockMovement).all()
        return [
            DomainMovement(
                id=m.id,
                inventory_id=m.inventory_id,
                movement_type=m.movement_type,
                quantity=m.quantity,
                reference_id=m.reference_id,
                created_at=m.created_at,
                created_by=m.created_by
            ) for m in db_movements
        ]
