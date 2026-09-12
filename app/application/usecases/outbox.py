from app.application.ports.messaging import EventPublisher
from app.application.ports.uow import UnitOfWorkFactory


class ProcessOutboxUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        publisher: EventPublisher,
        batch_size: int,
    ) -> None:
        self._uow_factory = uow_factory
        self._publisher = publisher
        self._batch_size = batch_size

    async def __call__(self) -> int:
        async with self._uow_factory() as uow:
            messages = await uow.outbox.get_pending_for_update(
                self._batch_size
            )

            for message in messages:
                if message.channel != "KAFKA":
                    raise ValueError(
                        f"Unsupported Outbox channel: {message.channel}"
                    )

                await self._publisher.publish(message)
                await uow.outbox.mark_as_sent(message.id)

            if messages:
                await uow.commit()

            return len(messages)