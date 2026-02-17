from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_stock_reservation_repository import IStockReservationRepository
from src.infrastructure.persistence.inventory.retry import retry_on_concurrency

class ReleaseExpiredReservationsHandler:
    def __init__(self, service: InventoryDomainService, reservation_repo: IStockReservationRepository):
        self.service = service
        self.reservation_repo = reservation_repo

    def execute(self):
        expired = self.reservation_repo.get_expired_reservations()
        for res in expired:
            self._release_one(res.id)

    @retry_on_concurrency(max_retries=3)
    def _release_one(self, reservation_id):
        self.service.release_reservation(reservation_id, reason="expired")
