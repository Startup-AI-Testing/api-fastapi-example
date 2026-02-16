from src.application.inventory.ports.i_inventory_unit_of_work import IInventoryUnitOfWork
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_event_publisher import IEventPublisher

class ReleaseExpiredReservationsHandler:
    def __init__(self, uow: IInventoryUnitOfWork, event_publisher: IEventPublisher):
        self.uow = uow
        self.event_publisher = event_publisher

    def execute(self):
        with self.uow:
            expired_ids = self.uow.reservation_repo.find_expired()
            
            domain_service = InventoryDomainService(
                inventory_repo=self.uow.inventory_repo,
                reservation_repo=self.uow.reservation_repo,
                movement_repo=self.uow.movement_repo,
                event_publisher=self.event_publisher
            )
            
            for reservation_id in expired_ids:
                try:
                    domain_service.release_reservation(reservation_id, reason="expired")
                except Exception:
                    # Log error but continue with others
                    pass
            
            self.uow.commit()
