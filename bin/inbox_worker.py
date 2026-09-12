import asyncio
import logging
from functools import partial

from app.application.usecases.inbox import ProcessInboxUseCase
from app.infrastructure.persistence.database import (
    create_engine_and_session_factory,
)
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.settings import Settings


async def main() -> None:
    settings = Settings()

    engine, session_factory = create_engine_and_session_factory(
        settings.database_url,
        settings.sql_echo,
    )

    try:
        use_case = ProcessInboxUseCase(
            uow_factory=partial(
                SqlAlchemyUnitOfWork,
                session_factory,
            ),
            batch_size=settings.inbox_batch_size,
        )

        while True:
            try:
                processed = await use_case()

                if processed == 0:
                    await asyncio.sleep(
                        settings.inbox_poll_interval
                    )
            except Exception:
                logging.exception("Inbox batch failed")
                await asyncio.sleep(
                    settings.inbox_poll_interval
                )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())