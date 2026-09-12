import asyncio
import json
import logging
from functools import partial
from typing import Any

from aiokafka import AIOKafkaConsumer

from app.application.usecases.inbox import SaveInboxEventUseCase
from app.infrastructure.persistence.database import (
    create_engine_and_session_factory,
)
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.settings import Settings

logger = logging.getLogger(__name__)


def make_event_key(
    event_type: str,
    payload: dict[str, Any],
    topic: str,
    partition: int,
    offset: int,
) -> str:
    order_id = payload.get("order_id")
    shipment_id = payload.get("shipment_id")

    if event_type == "order.shipped" and shipment_id:
        return f"order.shipped:shipment:{shipment_id}"

    if event_type == "order.cancelled" and order_id:
        return f"order.cancelled:order:{order_id}"

    return f"kafka:{topic}:{partition}:{offset}"


async def main() -> None:
    settings = Settings()

    engine, session_factory = create_engine_and_session_factory(
        settings.database_url,
        settings.sql_echo,
    )

    consumer = AIOKafkaConsumer(
        settings.kafka_shipment_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    save_inbox_event = SaveInboxEventUseCase(
        partial(SqlAlchemyUnitOfWork, session_factory)
    )

    await consumer.start()
    logger.info(
        "Shipment Consumer started; topic=%s",
        settings.kafka_shipment_topic,
    )

    try:
        async for message in consumer:
            try:
                payload = message.value
                event_type = str(payload["event_type"])

                if event_type not in {
                    "order.shipped",
                    "order.cancelled",
                }:
                    raise ValueError(
                        f"Unsupported shipment event: {event_type}"
                    )

                event_key = make_event_key(
                    event_type=event_type,
                    payload=payload,
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )

                created = await save_inbox_event(
                    event_key=event_key,
                    event_type=event_type,
                    payload=payload,
                )

                await consumer.commit()

                logger.info(
                    "Shipment event saved to Inbox; event_type=%s, new=%s",
                    event_type,
                    created,
                )
            except Exception:
                logger.exception(
                    "Shipment event was not saved; Kafka offset is not committed"
                )
                await asyncio.sleep(1)
    finally:
        await consumer.stop()
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())