from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    channel: str
    event_type: str
    payload: dict[str, object]
    idempotency_key: str
    created_at: datetime


@dataclass(frozen=True)
class InboxMessage:
    id: UUID
    event_key: str
    event_type: str
    payload: dict[str, object]
    created_at: datetime