from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from src.infrastructure.persistence.inventory.sql_inventory_repository import (
    SqlInventoryRepository,
    SqlStockReservationRepository,
    SqlStockMovementRepository
)
from src.infrastructure.external.event_publisher import ConsoleEventPublisher
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService

def get_inventory_service(db):
    inventory_repo = SqlInventoryRepository(db)
    reservation_repo = SqlStockReservationRepository(db)
    movement_repo = SqlStockMovementRepository(db)
    event_publisher = ConsoleEventPublisher()
    return InventoryDomainService(
        inventory_repo=inventory_repo,
        reservation_repo=reservation_repo,
        movement_repo=movement_repo,
        event_publisher=event_publisher
    )

def release_expired_reservations_job():
    db = SessionLocal()
    try:
        service = get_inventory_service(db)
        service.release_expired_reservations()
        db.commit()
    except Exception as e:
        print(f"Error in release_expired_reservations_job: {e}")
        db.rollback()
    finally:
        db.close()

def check_low_stock_job():
    db = SessionLocal()
    try:
        inventory_repo = SqlInventoryRepository(db)
        low_stock = inventory_repo.get_low_stock()
        for inv in low_stock:
            print(f"Low stock alert: Product {inv.product_id} has only {inv.quantity_available} units left.")
            # We could also publish a specific event here if needed
    except Exception as e:
        print(f"Error in check_low_stock_job: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 5 minutes as requested
    scheduler.add_job(release_expired_reservations_job, 'interval', minutes=5)
    # Run every hour as requested
    scheduler.add_job(check_low_stock_job, 'interval', hours=1)
    scheduler.start()
    return scheduler
