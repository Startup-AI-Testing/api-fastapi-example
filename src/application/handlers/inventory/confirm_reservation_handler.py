from src.domain.inventory.services.inventory_service import InventoryDomainService
import uuid

class ConfirmReservationHandler:
    def __init__(self, inventory_service: InventoryDomainService):
        self.inventory_service = inventory_service
        
    def execute(self, reservation_id: uuid.UUID, order_id: uuid.UUID):
        return self.inventory_service.confirm_reservation(reservation_id, order_id)
