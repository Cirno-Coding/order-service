import asyncio
import logging
from functools import partial

from app.application.usecases.outbox import ProcessOutboxUseCase
from app.infrastructure.messaging.kafka import KafkaEventPublisher
from app.infrastructure.persistence.database import (
    create_engine_and_session_factory,
)
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.settings import Settings

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings()

    engine, session_factory = create_engine_and_session_factory(
        settings.database_url,
        settings.sql_echo,
    )

    try:
        while True:
            try:
                async with KafkaEventPublisher(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    topic=settings.kafka_order_topic,
                    timeout_seconds=settings.kafka_publish_timeout,
                ) as publisher:
                    logger.info(
                        "Outbox Worker connected to Kafka: %s",
                        settings.kafka_bootstrap_servers,
                    )

                    use_case = ProcessOutboxUseCase(
                        uow_factory=partial(
                            SqlAlchemyUnitOfWork,
                            session_factory,
                        ),
                        publisher=publisher,
                        batch_size=settings.outbox_batch_size,
                    )

                    while True:
                        processed = await use_case()

                        if processed == 0:
                            await asyncio.sleep(
                                settings.outbox_poll_interval
                            )

                        logger.info(
                            "Outbox Worker processed %s messages",
                            processed,
                        )

            except Exception:
                logger.exception(
                    "Outbox Worker cannot connect to Kafka or process a batch"
                )

                await asyncio.sleep(settings.outbox_poll_interval)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(main())