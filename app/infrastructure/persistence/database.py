from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine


def create_engine_and_session_factory(
    database_url: str,
    echo: bool
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False
    )

    return engine, session_factory
