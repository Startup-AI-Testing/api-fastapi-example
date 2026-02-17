from abc import ABC, abstractmethod
from typing import Any

class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: Any) -> None:
        pass
