from ....domain.inventory.services.inventory_domain_service import InventoryDomainService

class ReleaseExpiredReservationsHandler:
    def __init__(self, service: InventoryDomainService):
        self.service = service

    def execute(self):
        # We need a method in the service to find and release expired reservations
        return self.service.release_expired_reservations()
