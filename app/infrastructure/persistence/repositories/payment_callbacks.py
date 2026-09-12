from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories import PaymentCallbackRepository
from app.infrastructure.persistence.models.events import PaymentCallbackModel


class SqlAlchemyPaymentCallbackRepository(PaymentCallbackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, payment_id: UUID) -> bool:
        callback = await self._session.get(PaymentCallbackModel, payment_id)
        return callback is not None

    async def add(
        self,
        payment_id: UUID,
        order_id: UUID,
        status: str,
    ) -> None:
        self._session.add(
            PaymentCallbackModel(
                payment_id=payment_id,
                order_id=order_id,
                status=status,
                received_at=datetime.now(UTC),
            )
        )