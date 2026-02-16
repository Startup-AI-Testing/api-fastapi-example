from src.domain.inventory.ports.i_event_publisher import IEventPublisher
import logging

logger = logging.getLogger(__name__)

class InMemoryEventPublisher(IEventPublisher):
    def publish(self, event) -> None:
        logger.info(f"Published event: {event}")
