from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

class AdjustStockHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(self, product_id: int, quantity: int, reason: str) -> None:
        self.inventory_service.adjust_stock(
            product_id=product_id,
            quantity=quantity,
            reason=reason
        )
