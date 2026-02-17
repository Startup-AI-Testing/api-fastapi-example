from dataclasses import dataclass
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.infrastructure.persistence.inventory.retry import retry_on_concurrency

@dataclass
class ReserveStockCommand:
    product_id: int
    quantity: int
    reservation_type: str = "order"

class ReserveStockHandler:
    def __init__(self, service: InventoryDomainService):
        self.service = service

    @retry_on_concurrency(max_retries=3)
    def execute(self, command: ReserveStockCommand):
        return self.service.reserve_stock(
            product_id=command.product_id,
            quantity=command.quantity,
            reservation_type=command.reservation_type
        )
