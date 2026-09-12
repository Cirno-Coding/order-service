from abc import ABC, abstractmethod

from app.application.dto.events import OutboxMessage


class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, message: OutboxMessage) -> None:
        pass