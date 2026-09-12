from datetime import datetime
from uuid import UUID

from sqlalchemy import Uuid, String, DateTime, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base import Base


class PaymentCallbackModel(Base):
    __tablename__ = "payment_callbacks"

    payment_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    order_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OutboxModel(Base):
    __tablename__ = "outbox"

    __table_args__ = (
        Index(
            "ix_outbox_pending_created_at",
            "created_at",
            "id",
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)

    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)

    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)

    idempotency_key: Mapped[str] = mapped_column(
        String(160),
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class InboxModel(Base):
    __tablename__ = "inbox"

    __table_args__ = (
        Index(
            "ix_inbox_pending_created_at",
            "created_at",
            "id",
            postgresql_where=text("status = 'PENDING'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)

    event_key: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
