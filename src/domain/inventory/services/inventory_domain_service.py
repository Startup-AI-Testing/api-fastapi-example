import uuid
from typing import Optional
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository
from src.domain.inventory.ports.i_event_publisher import IEventPublisher

from src.domain.inventory.events.inventory_events import (
    StockReserved, StockConfirmed, StockReleased, LowStockDetected, OutOfStock
)

from src.domain.inventory.errors.inventory_errors import (
    InsufficientStockError,
    InventoryNotFoundError,
    ReservationNotFoundError,
    ReservationExpiredError
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
            raise InventoryNotFoundError(f"Inventory for product {product_id} not found")

        inventory.reserve(quantity)
        
        reservation = StockReservation.create(
            id=uuid.uuid4(),
            inventory_id=product_id,
            quantity=quantity,
            reservation_type=reservation_type
        )
        
        movement = StockMovement.create(
            id=uuid.uuid4(),
            inventory_id=product_id,
            movement_type="reserve",
            quantity=-quantity,
            reference_id=reservation.id
        )

        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish(StockReserved(
            product_id=product_id,
            reservation_id=reservation.id,
            quantity=quantity
        ))

        if inventory.quantity_available == 0:
            self.event_publisher.publish(OutOfStock(product_id=product_id))
        elif inventory.quantity_available < inventory.reorder_point:
            self.event_publisher.publish(LowStockDetected(
                product_id=product_id,
                quantity_available=inventory.quantity_available,
                reorder_point=inventory.reorder_point
            ))
        
        return reservation

    def confirm_reservation(self, reservation_id: uuid.UUID, order_id: int) -> StockReservation:
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(f"Reservation {reservation_id} not found")

        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise InventoryNotFoundError(f"Inventory for product {reservation.inventory_id} not found")

        reservation.confirm(order_id)
        inventory.confirm_reservation(reservation.quantity)
        
        movement = StockMovement.create(
            id=uuid.uuid4(),
            inventory_id=inventory.product_id,
            movement_type="sale",
            quantity=0,
            reference_id=reservation.id
        )

        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish(StockConfirmed(
            product_id=inventory.product_id,
            reservation_id=reservation.id,
            order_id=order_id
        ))
        return reservation

    def release_reservation(self, reservation_id: uuid.UUID, reason: str = "released"):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFoundError(f"Reservation {reservation_id} not found")

        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise InventoryNotFoundError(f"Inventory for product {reservation.inventory_id} not found")

        reservation.release()
        inventory.release_reservation(reservation.quantity)
        
        movement = StockMovement.create(
            id=uuid.uuid4(),
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
            reservation_id=reservation.id,
            reason=reason
        ))


    def restock(self, product_id: int, quantity: int, created_by: str = "admin") -> Inventory:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(f"Inventory for product {product_id} not found")

        inventory.restock(quantity)
        
        movement = StockMovement.create(
            id=uuid.uuid4(),
            inventory_id=product_id,
            movement_type="restock",
            quantity=quantity,
            created_by=created_by
        )

        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        return inventory

    def adjust_stock(self, product_id: int, quantity: int, reason: str, created_by: str = "admin") -> Inventory:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise InventoryNotFoundError(f"Inventory for product {product_id} not found")

        inventory.adjust(quantity)
        
        movement = StockMovement.create(
            id=uuid.uuid4(),
            inventory_id=product_id,
            movement_type="adjustment",
            quantity=quantity,
            created_by=created_by
        )

        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        return inventory

    def check_availability(self, product_id: int, quantity: int) -> bool:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            return False
        return inventory.quantity_available >= quantity
