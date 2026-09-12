import asyncio
import json
from types import TracebackType
from typing import Self

from aiokafka import AIOKafkaProducer

from app.application.dto.events import OutboxMessage
from app.application.ports.messaging import EventPublisher


class KafkaEventPublisher(EventPublisher):
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        timeout_seconds: float,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic = topic
        self._timeout_seconds = timeout_seconds
        self._producer: AIOKafkaProducer | None = None

    async def __aenter__(self) -> Self:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            acks="all",
        )

        try:
            await self._producer.start()
        except BaseException:
            await self._producer.stop()
            self._producer = None
            raise

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(self, message: OutboxMessage) -> None:
        if self._producer is None:
            raise RuntimeError("Kafka publisher is not started")

        if message.payload.get("event_type") != message.event_type:
            raise ValueError(
                "Outbox event_type must match payload event_type"
            )

        async with asyncio.timeout(self._timeout_seconds):
            await self._producer.send_and_wait(
                self._topic,
                key=str(message.id).encode("utf-8"),
                value=json.dumps(
                    message.payload,
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8"),
            )