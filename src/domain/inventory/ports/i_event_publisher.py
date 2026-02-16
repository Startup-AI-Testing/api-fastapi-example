from abc import ABC, abstractmethod

class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: object) -> None:
        pass
