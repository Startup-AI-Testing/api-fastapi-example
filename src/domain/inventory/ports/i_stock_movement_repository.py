from abc import ABC, abstractmethod
from typing import List
from src.domain.inventory.entities.stock_movement import StockMovement

class IStockMovementRepository(ABC):
    @abstractmethod
    def save(self, movement: StockMovement) -> None:
        pass

    @abstractmethod
    def get_by_inventory_id(self, inventory_id: int) -> List[StockMovement]:
        pass
