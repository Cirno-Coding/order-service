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
        async with self._uow_factory() as uow:
            messages = await uow.outbox.get_pending_for_update(
                self._batch_size
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

            if messages:
                await uow.commit()

            return len(messages)