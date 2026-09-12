from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.events import OutboxMessage
from app.application.notification_messages import notification_text
from app.domain.entities import Order


def notification_message(
    order: Order,
    cancel_reason: str | None = None,
) -> OutboxMessage:
    idempotency_key = f"notification:{order.id}:{order.status.value}"

    return OutboxMessage(
        id=uuid4(),
        channel="NOTIFICATION",
        event_type="notification.send",
        idempotency_key=idempotency_key,
        created_at=datetime.now(UTC),
        payload={
            "message": notification_text(
                order.status,
                cancel_reason=cancel_reason,
            ),
            "reference_id": str(order.id),
            "idempotency_key": idempotency_key,
        },
    )


def order_paid_message(order: Order) -> OutboxMessage:
    idempotency_key = f"order-paid:{order.id}"

    return OutboxMessage(
        id=uuid4(),
        channel="KAFKA",
        event_type="order.paid",
        idempotency_key=idempotency_key,
        created_at=datetime.now(UTC),
        payload={
            "event_type": "order.paid",
            "order_id": str(order.id),
            "item_id": order.item_id,
            "quantity": order.quantity,
            "idempotency_key": order.idempotency_key,
        },
    )