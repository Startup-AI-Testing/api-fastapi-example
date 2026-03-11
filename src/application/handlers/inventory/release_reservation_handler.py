from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

class ReleaseReservationHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(self, reservation_id: str, reason: str = "manual") -> None:
        self.inventory_service.release_reservation(
            reservation_id=reservation_id,
            reason=reason
        )
