from uuid import UUID
from src.application.inventory.ports.i_inventory_unit_of_work import IInventoryUnitOfWork
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_event_publisher import IEventPublisher

class ConfirmReservationHandler:
    def __init__(self, uow: IInventoryUnitOfWork, event_publisher: IEventPublisher):
        self.uow = uow
        self.event_publisher = event_publisher

    def execute(self, reservation_id: UUID, order_id: str):
        with self.uow:
            domain_service = InventoryDomainService(
                inventory_repo=self.uow.inventory_repo,
                reservation_repo=self.uow.reservation_repo,
                movement_repo=self.uow.movement_repo,
                event_publisher=self.event_publisher
            )
            domain_service.confirm_reservation(reservation_id, order_id)
            self.uow.commit()
            return self.uow.reservation_repo.get_by_id(reservation_id)
