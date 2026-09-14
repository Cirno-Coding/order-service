from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import case, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.events import OutboxMessage
from app.application.ports.repositories import OutboxRepository
from app.infrastructure.persistence.models.events import OutboxModel


class SqlAlchemyOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, message: OutboxMessage) -> None:
        self._session.add(
            OutboxModel(
                id=message.id,
                channel=message.channel,
                event_type=message.event_type,
                payload=message.payload,
                idempotency_key=message.idempotency_key,
                status="PENDING",
                created_at=message.created_at,
            )
        )

    async def get_pending_for_update(
        self,
        limit: int,
    ) -> list[OutboxMessage]:
        channel_priority = case(
            (OutboxModel.channel == "KAFKA", 0),
            else_=1,
        )

        statement = (
            select(OutboxModel)
            .where(OutboxModel.status == "PENDING")
            .order_by(
                channel_priority,
                OutboxModel.created_at,
                OutboxModel.id,
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        rows = (await self._session.scalars(statement)).all()

        return [
            OutboxMessage(
                id=row.id,
                channel=row.channel,
                event_type=row.event_type,
                payload=row.payload,
                idempotency_key=row.idempotency_key,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def mark_as_sent(self, message_id: UUID) -> None:
        statement = (
            update(OutboxModel)
            .where(OutboxModel.id == message_id)
            .where(OutboxModel.status == "PENDING")
            .values(
                status="SENT",
                sent_at=datetime.now(UTC),
            )
        )

        await self._session.execute(statement)