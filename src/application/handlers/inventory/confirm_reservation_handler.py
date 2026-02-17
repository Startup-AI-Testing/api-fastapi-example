import uuid
from dataclasses import dataclass
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.infrastructure.persistence.inventory.retry import retry_on_concurrency

@dataclass
class ConfirmReservationCommand:
    reservation_id: uuid.UUID
    order_id: int

class ConfirmReservationHandler:
    def __init__(self, service: InventoryDomainService):
        self.service = service

    @retry_on_concurrency(max_retries=3)
    def execute(self, command: ConfirmReservationCommand):
        return self.service.confirm_reservation(
            reservation_id=command.reservation_id,
            order_id=command.order_id
        )
