from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

class ReleaseExpiredReservationsHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(self) -> None:
        self.inventory_service.release_expired_reservations()
