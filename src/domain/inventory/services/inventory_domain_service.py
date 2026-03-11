from uuid import UUID
from typing import Optional
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
from src.domain.inventory.ports.repository_ports import (
    IInventoryRepository, 
    IStockReservationRepository, 
    IStockMovementRepository,
    IEventPublisher
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

    def reserve_stock(
        self, 
        product_id: int, 
        quantity: int, 
        reservation_type: str = "cart"
    ) -> StockReservation:
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory for product {product_id} not found")

        inventory.reserve_stock(quantity)
        
        reservation = StockReservation.create(
            inventory_id=product_id, # Using product_id as inventory_id for simplicity if they are 1:1
            quantity=quantity,
            reservation_type=reservation_type
        )
        
        movement = StockMovement.create(
            inventory_id=product_id,
            movement_type="reserve",
            quantity=-quantity,
            reference_id=reservation.id
        )
        
        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish({
            "type": "StockReserved",
            "product_id": product_id,
            "quantity": quantity,
            "reservation_id": str(reservation.id)
        })
        
        if inventory.quantity_available < inventory.reorder_point:
            self.event_publisher.publish({
                "type": "LowStockDetected",
                "product_id": product_id,
                "available": inventory.quantity_available
            })
            
        return reservation

    def confirm_reservation(self, reservation_id: UUID, order_id: int):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory for product {reservation.inventory_id} not found")
        
        reservation.confirm(order_id)
        inventory.confirm_reservation(reservation.quantity)
        
        movement = StockMovement.create(
            inventory_id=inventory.product_id,
            movement_type="sale",
            quantity=0, # It was already decremented from available during reservation
            reference_id=reservation.id
        )
        
        self.inventory_repo.save(inventory)
        self.reservation_repo.save(reservation)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish({
            "type": "StockConfirmed",
            "product_id": inventory.product_id,
            "order_id": order_id,
            "quantity": reservation.quantity
        })

    def release_reservation(self, reservation_id: UUID, reason: str):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        inventory = self.inventory_repo.get_by_product_id(reservation.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory for product {reservation.inventory_id} not found")
        
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
        
        self.event_publisher.publish({
            "type": "StockReleased",
            "product_id": inventory.product_id,
            "reason": reason,
            "quantity": reservation.quantity
        })

    def restock(self, product_id: int, quantity: int, reference: str = None, created_by: str = "admin"):
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            # Create inventory if it doesn't exist
            inventory = Inventory.create(product_id=product_id)
        
        inventory.restock(quantity)
        
        movement = StockMovement.create(
            inventory_id=product_id,
            movement_type="restock",
            quantity=quantity,
            reference_id=reference,
            created_by=created_by
        )
        
        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish({
            "type": "StockRestocked",
            "product_id": product_id,
            "quantity": quantity
        })

    def adjust_stock(self, product_id: int, quantity: int, reason: str, created_by: str = "admin"):
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            raise ValueError(f"Inventory for product {product_id} not found")
        
        inventory.adjust_stock(quantity)
        
        movement = StockMovement.create(
            inventory_id=product_id,
            movement_type="adjustment",
            quantity=quantity,
            created_by=created_by
        )
        
        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish({
            "type": "StockAdjusted",
            "product_id": product_id,
            "quantity": quantity,
            "reason": reason
        })

    def release_expired_reservations(self):
        expired = self.reservation_repo.get_expired_reservations()
        for reservation in expired:
            self.release_reservation(reservation.id, reason="expired")

    def release_order_stock(self, order_id: int, product_id: int, quantity: int):
        """Release stock from a cancelled order."""
        inventory = self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            return

        inventory.quantity_sold -= quantity
        inventory.quantity_available += quantity
        
        movement = StockMovement.create(
            inventory_id=product_id,
            movement_type="release",
            quantity=quantity,
            reference_id=str(order_id),
            created_by="system"
        )
        
        self.inventory_repo.save(inventory)
        self.movement_repo.save(movement)
        
        self.event_publisher.publish({
            "type": "StockReleased",
            "product_id": product_id,
            "order_id": order_id,
            "quantity": quantity,
            "reason": "order_cancelled"
        })
