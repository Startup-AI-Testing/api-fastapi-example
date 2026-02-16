from apscheduler.schedulers.background import BackgroundScheduler
from src.infrastructure.jobs.inventory_jobs import release_expired_reservations_job, check_low_stock_job
import logging

logger = logging.getLogger(__name__)

def setup_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run every 5 minutes
    scheduler.add_job(
        release_expired_reservations_job,
        'interval',
        minutes=5,
        id='release_expired_reservations',
        replace_existing=True
    )
    
    # Run every hour
    scheduler.add_job(
        check_low_stock_job,
        'interval',
        hours=1,
        id='check_low_stock',
        replace_existing=True
    )
    
    return scheduler

def start_scheduler():
    logger.info("Starting background scheduler")
    scheduler = setup_scheduler()
    scheduler.start()
    return scheduler
