from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import partial

import httpx
from fastapi import FastAPI

from app.infrastructure.http.catalog import CapashinoCatalogClient
from app.infrastructure.http.payments import CapashinoPaymentsClient
from app.infrastructure.persistence.database import (
    create_engine_and_session_factory,
)
from app.infrastructure.persistence.uow import SqlAlchemyUnitOfWork
from app.presentation.api.errors import register_error_handlers
from app.presentation.api.routes.health import router as health_router
from app.presentation.api.routes.orders import router as orders_router
from app.presentation.api.routes.payment_callback import (
    router as payment_callback_router,
)
from app.settings import Settings


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        settings = Settings()

        engine, session_factory = create_engine_and_session_factory(
            database_url=settings.database_url,
            echo=settings.sql_echo,
        )

        http_client = httpx.AsyncClient(timeout=10)

        app.state.settings = settings
        app.state.uow_factory = partial(
            SqlAlchemyUnitOfWork,
            session_factory,
        )

        app.state.catalog_gateway = CapashinoCatalogClient(
            client=http_client,
            base_url=settings.capashino_base_url,
            api_key=settings.capashino_api_key,
        )

        app.state.payments_gateway = CapashinoPaymentsClient(
            client=http_client,
            base_url=settings.capashino_base_url,
            api_key=settings.capashino_api_key,
        )

        try:
            yield
        finally:
            await http_client.aclose()
            await engine.dispose()

    app = FastAPI(
        title="Order Service Capashino",
        version="0.4.0",
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(orders_router)
    app.include_router(payment_callback_router)

    register_error_handlers(app)

    return app


app = create_app()
