from src.application.inventory.ports.i_inventory_unit_of_work import IInventoryUnitOfWork
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_event_publisher import IEventPublisher

class RestockHandler:
    def __init__(self, uow: IInventoryUnitOfWork, event_publisher: IEventPublisher):
        self.uow = uow
        self.event_publisher = event_publisher

    def execute(self, product_id: int, quantity: int, created_by: str = "system"):
        with self.uow:
            domain_service = InventoryDomainService(
                inventory_repo=self.uow.inventory_repo,
                reservation_repo=self.uow.reservation_repo,
                movement_repo=self.uow.movement_repo,
                event_publisher=self.event_publisher
            )
            domain_service.restock(product_id, quantity, created_by)
            self.uow.commit()
