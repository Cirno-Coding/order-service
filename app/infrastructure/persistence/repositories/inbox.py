from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.events import InboxMessage
from app.application.ports.repositories import InboxRepository
from app.infrastructure.persistence.models.events import InboxModel


class SqlAlchemyInboxRepository(InboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_if_absent(self, message: InboxMessage) -> bool:
        statement = (
            insert(InboxModel)
            .values(
                id=message.id,
                event_key=message.event_key,
                event_type=message.event_type,
                payload=message.payload,
                status="PENDING",
                created_at=message.created_at,
            )
            .on_conflict_do_nothing(
                index_elements=[InboxModel.event_key]
            )
            .returning(InboxModel.id)
        )

        created_id = await self._session.scalar(statement)

        return created_id is not None

    async def get_pending_for_update(
        self,
        limit: int,
    ) -> list[InboxMessage]:
        statement = (
            select(InboxModel)
            .where(InboxModel.status == "PENDING")
            .order_by(InboxModel.created_at, InboxModel.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        rows = (await self._session.scalars(statement)).all()

        return [
            InboxMessage(
                id=row.id,
                event_key=row.event_key,
                event_type=row.event_type,
                payload=row.payload,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def mark_as_processed(self, message_id: UUID) -> None:
        statement = (
            update(InboxModel)
            .where(InboxModel.id == message_id)
            .where(InboxModel.status == "PENDING")
            .values(
                status="PROCESSED",
                processed_at=datetime.now(UTC),
            )
        )

        await self._session.execute(statement)