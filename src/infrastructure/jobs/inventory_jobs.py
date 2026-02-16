import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from src.infrastructure.persistence.inventory.sql_inventory_repository import SqlInventoryRepository
from src.infrastructure.persistence.inventory.sql_stock_reservation_repository import SqlStockReservationRepository
from src.infrastructure.persistence.inventory.sql_stock_movement_repository import SqlStockMovementRepository
from src.infrastructure.persistence.inventory.in_memory_event_publisher import InMemoryEventPublisher
from src.domain.inventory.services.inventory_domain_service import InventoryDomainService
from app.models import StockReservation as StockReservationORM
from datetime import datetime

logger = logging.getLogger(__name__)

def release_expired_reservations_job(db_session: Session = None):
    logger.info("Running release_expired_reservations_job")
    db = db_session or SessionLocal()
    try:
        # Find expired active reservations
        now = datetime.utcnow()
        expired_reservations = db.query(StockReservationORM).filter(
            StockReservationORM.status == "active",
            StockReservationORM.expires_at < now
        ).all()
        
        if not expired_reservations:
            return

        logger.info(f"Found {len(expired_reservations)} expired reservations")
        
        # Setup service
        inventory_repo = SqlInventoryRepository(db)
        reservation_repo = SqlStockReservationRepository(db)
        movement_repo = SqlStockMovementRepository(db)
        event_publisher = InMemoryEventPublisher()
        
        service = InventoryDomainService(
            inventory_repo,
            reservation_repo,
            movement_repo,
            event_publisher
        )
        
        for res in expired_reservations:
            try:
                import uuid
                service.release_reservation(uuid.UUID(str(res.id)), "Expired")
                logger.info(f"Released expired reservation {res.id}")
            except Exception as e:
                logger.error(f"Error releasing expired reservation {res.id}: {e}")
        
        db.commit()
    except Exception as e:
        logger.error(f"Error in release_expired_reservations_job: {e}")
        db.rollback()
    finally:
        if db_session is None:
            db.close()

def check_low_stock_job(db_session: Session = None):
    logger.info("Running check_low_stock_job")
    db = db_session or SessionLocal()
    try:
        from app.models import Inventory as InventoryORM
        low_stock_items = db.query(InventoryORM).filter(
            InventoryORM.quantity_available < InventoryORM.reorder_point
        ).all()
        
        for item in low_stock_items:
            logger.warning(f"Low stock detected for product {item.product_id}: {item.quantity_available} available")
    finally:
        if db_session is None:
            db.close()
