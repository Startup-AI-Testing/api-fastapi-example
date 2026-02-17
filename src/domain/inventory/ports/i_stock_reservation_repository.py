from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from src.domain.inventory.entities.stock_reservation import StockReservation

class IStockReservationRepository(ABC):
    @abstractmethod
    def get_by_id(self, reservation_id: uuid.UUID) -> Optional[StockReservation]:
        pass

    @abstractmethod
    def save(self, reservation: StockReservation) -> None:
        pass

    @abstractmethod
    def get_expired_reservations(self) -> List[StockReservation]:
        pass
