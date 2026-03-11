from src.domain.inventory.ports.repository_ports import IEventPublisher

class ConsoleEventPublisher(IEventPublisher):
    def publish(self, event: dict) -> None:
        print(f"Event published: {event}")
