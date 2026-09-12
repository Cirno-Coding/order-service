import asyncio

from app.infrastructure.persistence.database import create_engine_and_session_factory
from app.infrastructure.persistence.models import Base
from app.settings import Settings


async def main() -> None:
    settings = Settings()

    engine, _ = create_engine_and_session_factory(
        database_url=settings.database_url,
        echo=settings.sql_echo,
    )

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        print(
            "Tables are ready: "
            "orders, order_statuses, payment_callbacks, outbox, inbox"
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())