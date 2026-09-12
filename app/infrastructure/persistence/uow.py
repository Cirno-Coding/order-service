from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.uow import UnitOfWork
from app.infrastructure.persistence.repositories.inbox import SqlAlchemyInboxRepository
from app.infrastructure.persistence.repositories.orders import SqlAlchemyOrderRepository
from app.infrastructure.persistence.repositories.outbox import SqlAlchemyOutboxRepository
from app.infrastructure.persistence.repositories.payment_callbacks import SqlAlchemyPaymentCallbackRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()

        self.orders = SqlAlchemyOrderRepository(self._session)

        self.payment_callbacks = SqlAlchemyPaymentCallbackRepository(
            self._session
        )

        self.outbox = SqlAlchemyOutboxRepository(self._session)
        self.inbox = SqlAlchemyInboxRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            # Если commit не был вызван, изменения откатятся.
            await self._session.rollback()
        finally:
            await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()