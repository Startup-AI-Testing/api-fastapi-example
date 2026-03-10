from src.domain.inventory.services.inventory_service import InventoryDomainService

class ReserveStockHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service
        
    def execute(self, product_id: int, quantity: int, reservation_type: str):
        return self.inventory_service.reserve_stock(product_id, quantity, reservation_type)
