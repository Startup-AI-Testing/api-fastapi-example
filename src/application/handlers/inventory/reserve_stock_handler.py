from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.entities.stock_reservation import StockReservation

class ReserveStockHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service

    def execute(
        self, 
        product_id: int, 
        quantity: int, 
        reservation_type: str = "cart"
    ) -> StockReservation:
        return self.inventory_service.reserve_stock(
            product_id=product_id,
            quantity=quantity,
            reservation_type=reservation_type
        )
