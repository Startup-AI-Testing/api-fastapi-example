from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

class RestockHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(self, product_id: int, quantity: int, reference: str) -> None:
        self.inventory_service.restock(
            product_id=product_id,
            quantity=quantity,
            reference=reference
        )
