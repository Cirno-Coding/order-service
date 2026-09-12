from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dto.events import InboxMessage, OutboxMessage
from app.domain.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        pass

    @abstractmethod
    async def get_by_id_for_update(
        self,
        order_id: UUID,
    ) -> Order | None:
        pass

    @abstractmethod
    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Order | None:
        pass

    @abstractmethod
    async def update(self, order: Order) -> None:
        pass


class PaymentCallbackRepository(ABC):
    @abstractmethod
    async def exists(self, payment_id: UUID) -> bool:
        pass

    @abstractmethod
    async def add(
        self,
        payment_id: UUID,
        order_id: UUID,
        status: str,
    ) -> None:
        pass


class OutboxRepository(ABC):
    @abstractmethod
    async def add(self, message: OutboxMessage) -> None:
        pass

    @abstractmethod
    async def get_pending_for_update(
        self,
        limit: int,
    ) -> list[OutboxMessage]:
        pass

    @abstractmethod
    async def mark_as_sent(self, message_id: UUID) -> None:
        pass


class InboxRepository(ABC):
    @abstractmethod
    async def add_if_absent(self, message: InboxMessage) -> bool:
        pass

    @abstractmethod
    async def get_pending_for_update(
        self,
        limit: int,
    ) -> list[InboxMessage]:
        pass

    @abstractmethod
    async def mark_as_processed(self, message_id: UUID) -> None:
        pass