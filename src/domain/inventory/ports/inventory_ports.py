from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.entities.stock_reservation import StockReservation
from src.domain.inventory.entities.stock_movement import StockMovement
import uuid

class IInventoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, inventory_id: int) -> Optional[Inventory]:
        pass

    @abstractmethod
    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        pass

    @abstractmethod
    def save(self, inventory: Inventory) -> None:
        pass

    @abstractmethod
    def get_low_stock(self) -> List[Inventory]:
        pass

class IStockReservationRepository(ABC):
    @abstractmethod
    def get_by_id(self, reservation_id: str) -> Optional[StockReservation]:
        pass

    @abstractmethod
    def save(self, reservation: StockReservation) -> None:
        pass

    @abstractmethod
    def get_expired_reservations(self) -> List[StockReservation]:
        pass

class IStockMovementRepository(ABC):
    @abstractmethod
    def save(self, movement: StockMovement) -> None:
        pass

    @abstractmethod
    def get_by_inventory_id(self, inventory_id: int) -> List[StockMovement]:
        pass

    @abstractmethod
    def get_all(self) -> List[StockMovement]:
        pass

class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: any) -> None:
        pass
