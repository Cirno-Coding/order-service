from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import Self

from app.application.ports.repositories import (
    OrderRepository,
    PaymentCallbackRepository,
)


class UnitOfWork(ABC):
    orders: OrderRepository
    payment_callbacks: PaymentCallbackRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass


UnitOfWorkFactory = Callable[[], UnitOfWork]