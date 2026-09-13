from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.events import InboxMessage
from app.application.outbox_messages import notification_message
from app.application.ports.uow import UnitOfWorkFactory
from app.domain.entities import OrderStatus


class SaveInboxEventUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(
        self,
        event_key: str,
        event_type: str,
        payload: dict[str, object],
    ) -> bool:
        message = InboxMessage(
            id=uuid4(),
            event_key=event_key,
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(UTC),
        )

        async with self._uow_factory() as uow:
            created = await uow.inbox.add_if_absent(message)

            if created:
                await uow.commit()

            return created


class ProcessInboxUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        batch_size: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._batch_size = batch_size

    async def __call__(self) -> int:
        processed_count = 0

        async with self._uow_factory() as uow:
            messages = await uow.inbox.get_pending_for_update(
                self._batch_size
            )

            for message in messages:
                order_id = UUID(str(message.payload["order_id"]))

                order = await uow.orders.get_by_id_for_update(order_id)

                # Событие другого студента из общего Kafka-топика.
                if order is None:
                    await uow.inbox.mark_as_processed(message.id)
                    processed_count += 1
                    continue

                if message.event_type == "order.shipped":
                    if order.status == OrderStatus.NEW:
                        # Событие пришло раньше успешной оплаты.
                        # Оставляем его PENDING для повторной попытки.
                        continue

                    if order.status == OrderStatus.PAID:
                        order.ship()

                        await uow.orders.update(order)

                        await uow.outbox.add(
                            notification_message(order)
                        )

                    # При SHIPPED или CANCELLED событие устарело либо
                    # дублируется. Повторно менять статус не нужно.
                    await uow.inbox.mark_as_processed(message.id)
                    processed_count += 1

                elif message.event_type == "order.cancelled":
                    if order.status in {
                        OrderStatus.NEW,
                        OrderStatus.PAID,
                    }:
                        order.cancel()

                        cancel_reason = message.payload.get("reason")

                        if not isinstance(cancel_reason, str):
                            cancel_reason = (
                                "Товар недоступен для доставки"
                            )

                        await uow.orders.update(order)

                        await uow.outbox.add(
                            notification_message(
                                order,
                                cancel_reason=cancel_reason,
                            )
                        )

                    # Для CANCELLED и SHIPPED повторное/устаревшее
                    # событие просто считаем обработанным.
                    await uow.inbox.mark_as_processed(message.id)
                    processed_count += 1

                else:
                    raise ValueError(
                        f"Unsupported shipment event: "
                        f"{message.event_type}"
                    )

            if processed_count:
                await uow.commit()

        return processed_count