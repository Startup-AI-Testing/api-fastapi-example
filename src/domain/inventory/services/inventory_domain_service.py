import uuid
from typing import Optional
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository
from src.domain.inventory.ports.i_event_publisher import IEventPublisher
from src.domain.inventory.errors.inventory_errors import (
    InsufficientStockError,
    InventoryNotFoundError,
    ReservationNotFoundError
)
from src.domain.inventory.events.inventory_events import (
    StockReserved,
    StockConfirmed,
    StockReleased,
    LowStockDetected,
    OutOfStock
)

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

    def reserve_stock(self, product_id: int, quantity: int, reservation_type: str = "order") -> StockReservation:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(product_id)

        if not inventory.can_reserve(quantity):
            raise InsufficientStockError(product_id, quantity, inventory.quantity_available)

        inventory.reserve(quantity)
        reservation = StockReservation.create(
            inventory_id=inventory.id,
            quantity=quantity,
            reservation_type=reservation_type
        )

        movement = StockMovement.create(
            inventory_id=inventory.id,
            movement_type="reserve",
            quantity=-quantity,
            reference_id=reservation.id
        )

        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)

        self.event_publisher.publish(StockReserved(
            inventory_id=inventory.id,
            product_id=product_id,
            quantity=quantity,
            reservation_id=reservation.id
        ))

        if inventory.is_low_stock():
            self.event_publisher.publish(LowStockDetected(
                product_id=product_id,
                quantity_available=inventory.quantity_available,
                reorder_point=inventory.reorder_point
            ))
        
        if inventory.quantity_available == 0:
            self.event_publisher.publish(OutOfStock(product_id=product_id))

        return reservation

    def confirm_reservation(self, reservation_id: uuid.UUID, order_id: int) -> None:
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        inventory = self.inventory_repo.get_by_id(reservation.inventory_id)
        if not inventory:
            # This should not happen if data is consistent
            raise InventoryNotFoundError(0) # Generic or specific error

        inventory.confirm_reservation(reservation.quantity)
        reservation.confirm(order_id)

        movement = StockMovement.create(
            inventory_id=inventory.id,
            movement_type="sale",
            quantity=0, # It was already reserved, but we log the sale
            reference_id=uuid.UUID(str(reservation_id)) # Just for reference
        )

        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)

        self.event_publisher.publish(StockConfirmed(
            inventory_id=inventory.id,
            product_id=inventory.product_id,
            quantity=reservation.quantity,
            reservation_id=reservation.id,
            order_id=order_id
        ))

    def release_reservation(self, reservation_id: uuid.UUID, reason: str) -> None:
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(reservation_id)

        if reservation.status not in ["active", "confirmed"]:
            return # Already released or expired

        inventory = self.inventory_repo.get_by_id(reservation.inventory_id)
        if not inventory:
            raise InventoryNotFoundError(0)

        if reservation.status == "confirmed":
            # If it was confirmed, it was moved from reserved to sold
            inventory.quantity_sold -= reservation.quantity
            inventory.quantity_available += reservation.quantity
        else:
            # If it was active, it was in reserved
            inventory.release_reservation(reservation.quantity)
            
        reservation.release()

        movement = StockMovement.create(
            inventory_id=inventory.id,
            movement_type="release",
            quantity=reservation.quantity,
            reference_id=reservation.id
        )

        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)

        self.event_publisher.publish(StockReleased(
            inventory_id=inventory.id,
            product_id=inventory.product_id,
            quantity=reservation.quantity,
            reservation_id=reservation.id,
            reason=reason
        ))

    def restock(self, product_id: int, quantity: int, reference: str = "restock") -> None:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(product_id)

        inventory.restock(quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.id,
            movement_type="restock",
            quantity=quantity,
            created_by=reference
        )

        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)

    def adjust_stock(self, product_id: int, quantity: int, reason: str, created_by: str = "system") -> Inventory:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(product_id)

        inventory.quantity_available += quantity
        if inventory.quantity_available < 0:
            inventory.quantity_available = 0

        movement = StockMovement.create(
            inventory_id=inventory.id,
            movement_type="adjustment",
            quantity=quantity,
            created_by=f"{reason} - {created_by}"
        )

        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        return inventory
