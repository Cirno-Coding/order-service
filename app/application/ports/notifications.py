from abc import ABC, abstractmethod


class NotificationsGateway(ABC):
    @abstractmethod
    async def send(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> None:
        pass