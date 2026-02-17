from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.persistence.inventory.sql_stock_movement_repository import SqlStockMovementRepository
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from src.application.handlers.inventory.release_expired_reservations_handler import ReleaseExpiredReservationsHandler
from src.infrastructure.external.event_publisher import InMemoryEventPublisher

# We can use a shared event publisher or a real one
event_publisher = InMemoryEventPublisher()

def release_expired_reservations_job(handler=None):
    if handler is None:
        db = SessionLocal()
        try:
            inventory_repo = SqlInventoryRepository(db)
            reservation_repo = SqlStockReservationRepository(db)
            movement_repo = SqlStockMovementRepository(db)
            service = InventoryDomainService(inventory_repo, reservation_repo, movement_repo, event_publisher)
            handler = ReleaseExpiredReservationsHandler(service, reservation_repo)
            handler.execute()
            db.commit()
        except Exception as e:
            print(f"Error in release_expired_reservations_job: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        handler.execute()

def check_low_stock_job():
    db = SessionLocal()
    try:
        inventory_repo = SqlInventoryRepository(db)
        low_stock_items = inventory_repo.find_low_stock()
        for item in low_stock_items:
            # Emit event for each low stock item
            # In a real system, this would trigger a notification
            print(f"Low stock detected for product {item.product_id}: {item.quantity_available}")
    except Exception as e:
        print(f"Error in check_low_stock_job: {e}")
    finally:
        db.close()

def start_inventory_jobs():
    scheduler = BackgroundScheduler()
    scheduler.add_job(release_expired_reservations_job, 'interval', minutes=5)
    scheduler.add_job(check_low_stock_job, 'interval', hours=1)
    scheduler.start()
    return scheduler
