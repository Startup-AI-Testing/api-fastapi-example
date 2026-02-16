from abc import ABC, abstractmethod
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.domain.inventory.ports.i_stock_movement_repository import IStockMovementRepository

class IInventoryUnitOfWork(ABC):
    inventory_repo: IInventoryRepository
    reservation_repo: IStockReservationRepository
    movement_repo: IStockMovementRepository

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
