from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.inventory.entities.inventory import Inventory

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
    def list_low_stock(self) -> List[Inventory]:
        pass
