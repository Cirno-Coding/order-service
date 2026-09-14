from app.application.ports.messaging import EventPublisher
from app.application.ports.notifications import NotificationsGateway
from app.application.ports.uow import UnitOfWorkFactory


class ProcessOutboxUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        event_publisher: EventPublisher,
        notifications_gateway: NotificationsGateway,
        batch_size: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._event_publisher = event_publisher
        self._notifications_gateway = notifications_gateway
        self._batch_size = batch_size

    async def __call__(self) -> int:
        processed_count = 0

        async with self._uow_factory() as uow:
            messages = await uow.outbox.get_pending_for_update(
                self._batch_size
            )

            # Публикация order.paid важнее отправки уведомлений:
            # временная ошибка Notifications не должна блокировать Shipping.
            messages.sort(
                key=lambda message: message.channel != "KAFKA"
            )

            for message in messages:
                if message.channel == "KAFKA":
                    await self._event_publisher.publish(message)

                elif message.channel == "NOTIFICATION":
                    await self._notifications_gateway.send(
                        message=str(message.payload["message"]),
                        reference_id=str(
                            message.payload["reference_id"]
                        ),
                        idempotency_key=str(
                            message.payload["idempotency_key"]
                        ),
                    )

                else:
                    raise ValueError(
                        f"Unsupported Outbox channel: {message.channel}"
                    )

                await uow.outbox.mark_as_sent(message.id)

                # Фиксируем каждое сообщение отдельно. Если внешний
                # Notifications Service вернёт 500, уже опубликованное
                # Kafka-событие не откатится.
                await uow.commit()

                processed_count += 1

        return processed_count