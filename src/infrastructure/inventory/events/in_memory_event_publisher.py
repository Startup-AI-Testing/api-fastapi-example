from src.domain.inventory.ports.i_event_publisher import IEventPublisher

class InMemoryEventPublisher(IEventPublisher):
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)
        print(f"Published event: {event}")
