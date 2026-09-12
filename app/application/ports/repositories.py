from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        pass

    @abstractmethod
    async def get_by_id_for_update(self, order_id: UUID) -> Order | None:
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