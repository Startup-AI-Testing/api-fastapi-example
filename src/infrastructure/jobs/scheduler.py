from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from ..persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from ..persistence.inventory.sql_inventory_repository import SqlStockReservationRepository
from ..persistence.inventory.sql_inventory_repository import SqlStockMovementRepository
from ...domain.inventory.services.inventory_service import InventoryDomainService
from ...domain.inventory.ports.inventory_ports import IEventPublisher

class ConsoleEventPublisher(IEventPublisher):
    def publish(self, event):
        print(f"Event published: {event}")

def release_expired_reservations_job():
    db = SessionLocal()
    try:
        inventory_repo = SqlInventoryRepository(db)
        reservation_repo = SqlStockReservationRepository(db)
        movement_repo = SqlStockMovementRepository(db)
        event_publisher = ConsoleEventPublisher()
        
        service = InventoryDomainService(
            inventory_repo, 
            reservation_repo, 
            movement_repo,
            event_publisher
        )
        
        count = service.release_expired_reservations()
        if count > 0:
            print(f"Released {count} expired reservations")
    finally:
        db.close()

def check_low_stock_job():
    db = SessionLocal()
    try:
        inventory_repo = SqlInventoryRepository(db)
        low_stock = inventory_repo.get_low_stock()
        for inv in low_stock:
            print(f"Low stock detected for product {inv.product_id}: {inv.quantity_available}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(release_expired_reservations_job, 'interval', minutes=5)
    scheduler.add_job(check_low_stock_job, 'interval', hours=1)
    scheduler.start()
    return scheduler
