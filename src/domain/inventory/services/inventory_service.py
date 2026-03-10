from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.domain.inventory.ports.inventory_ports import (
    IInventoryRepository,
    IStockReservationRepository,
    IStockMovementRepository,
    IEventPublisher
)
from src.domain.inventory.events.inventory_events import (
    StockReserved,
    StockConfirmed,
    StockReleased,
    LowStockDetected,
    OutOfStock
)
import uuid
from typing import Optional

class InventoryDomainService:
    def __init__(
        self,
        inventory_repo: IInventoryRepository,
        reservation_repo: IStockReservationRepository,
        movement_repo: IStockMovementRepository,
        event_publisher: IEventPublisher
    ):
        self.inventory_repo = inventory_repo
        self.reservation_repo = reservation_repo
        self.movement_repo = movement_repo
        self.event_publisher = event_publisher

    def _check_stock_events(self, inventory: Inventory):
        if inventory.quantity_available == 0:
            self.event_publisher.publish(OutOfStock(product_id=inventory.product_id))
        elif inventory.quantity_available < inventory.reorder_point:
            self.event_publisher.publish(LowStockDetected(
                product_id=inventory.product_id,
                quantity_available=inventory.quantity_available,
                reorder_point=inventory.reorder_point
            ))

    def reserve_stock(self, product_id: int, quantity: int, reservation_type: str = "order") -> StockReservation:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id}")
        
        inventory.reserve(quantity)
        
        reservation = StockReservation.create(
            inventory_id=inventory.product_id,
            quantity=quantity,
            reservation_type=reservation_type
        )
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="reserve",
            quantity=-quantity,
            reference_id=reservation.id
        )
        
        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish(StockReserved(
            product_id=product_id,
            quantity=quantity,
            reservation_id=reservation.id
        ))
        
        self._check_stock_events(inventory)
        return reservation

    def release_expired_reservations(self):
        expired = self.reservation_repo.get_expired_reservations()
        released_count = 0
        for reservation in expired:
            try:
                self.release_reservation(reservation.id, reason="Expired")
                released_count += 1
            except Exception:
                # Log error or continue
                pass
        return released_count

    def confirm_reservation(self, reservation_id: str, order_id: str):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory not found for reservation {reservation_id}")
        
        reservation.confirm(order_id)
        inventory.confirm_reservation(reservation.quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="sale",
            quantity=-reservation.quantity,
            reference_id=reservation.id
        )
        
        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish(StockConfirmed(
            product_id=inventory.product_id,
            quantity=reservation.quantity,
            order_id=order_id
        ))

    def release_reservation(self, reservation_id: str, reason: str):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory not found for reservation {reservation_id}")
        
        reservation.release()
        inventory.release_reservation(reservation.quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="release",
            quantity=reservation.quantity,
            reference_id=reservation.id
        )
        
        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish(StockReleased(
            product_id=inventory.product_id,
            quantity=reservation.quantity,
            reason=reason
        ))
        
        self._check_stock_events(inventory)

    def check_availability(self, product_id: int, quantity: int) -> bool:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            return False
        return inventory.quantity_available >= quantity

    def restock(self, product_id: int, quantity: int, created_by: str = "system"):
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            inventory = Inventory.create(product_id=product_id, quantity_available=0)
        
        inventory.restock(quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="restock",
            quantity=quantity,
            created_by=created_by
        )
        
        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        
        self._check_stock_events(inventory)

    def adjust_stock(self, product_id: int, quantity: int, reason: str, created_by: str = "system"):
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id}")
        
        inventory.adjust_stock(quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="adjustment",
            quantity=quantity,
            created_by=created_by
        )
        
        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        
        self._check_stock_events(inventory)
