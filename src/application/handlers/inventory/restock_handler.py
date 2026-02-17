from dataclasses import dataclass
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.infrastructure.persistence.inventory.retry import retry_on_concurrency

@dataclass
class RestockCommand:
    product_id: int
    quantity: int
    created_by: str = "admin"

class RestockHandler:
    def __init__(self, service: InventoryDomainService):
        self.service = service

    @retry_on_concurrency(max_retries=3)
    def execute(self, command: RestockCommand):
        return self.service.restock(
            product_id=command.product_id,
            quantity=command.quantity,
            created_by=command.created_by
        )
