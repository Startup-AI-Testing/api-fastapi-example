from abc import ABC, abstractmethod
from src.domain.inventory.entities.stock_movement import StockMovement

class IStockMovementRepository(ABC):
    @abstractmethod
    def save(self, movement: StockMovement) -> None:
        pass
