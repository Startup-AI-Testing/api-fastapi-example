import time
from src.application.inventory.ports.i_inventory_unit_of_work import IInventoryUnitOfWork
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.domain.inventory.ports.i_event_publisher import IEventPublisher

class ReserveStockHandler:
    def __init__(
        self, 
        uow: IInventoryUnitOfWork, 
        event_publisher: IEventPublisher,
        max_retries: int = 3
    ):
        self.uow = uow
        self.event_publisher = event_publisher
        self.max_retries = max_retries

    def execute(self, product_id: int, quantity: int, reservation_type: str = "order"):
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                with self.uow:
                    domain_service = InventoryDomainService(
                        inventory_repo=self.uow.inventory_repo,
                        reservation_repo=self.uow.reservation_repo,
                        movement_repo=self.uow.movement_repo,
                        event_publisher=self.event_publisher
                    )
                    reservation = domain_service.reserve_stock(product_id, quantity, reservation_type)
                    self.uow.commit()
                    return reservation
            except Exception as e:
                # In a real app, we would check for a specific ConcurrencyException
                if "Concurrency conflict" in str(e):
                    last_exception = e
                    time.sleep(0.1 * (attempt + 1)) # Exponential backoff
                    continue
                raise e
        
        raise last_exception
