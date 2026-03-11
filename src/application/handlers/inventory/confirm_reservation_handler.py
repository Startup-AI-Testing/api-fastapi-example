from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

class ConfirmReservationHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(self, reservation_id: str, order_id: int) -> None:
        self.inventory_service.confirm_reservation(
            reservation_id=reservation_id,
            order_id=order_id
        )
