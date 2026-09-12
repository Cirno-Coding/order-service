from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.exceptions import (
    CatalogItemNotFoundError,
    ExternalServiceError,
    InsufficientStockError,
    OrderNotFoundError,
)
from app.domain.exceptions import (
    InvalidOrderError,
    InvalidStatusTransitionError,
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(OrderNotFoundError)
    async def order_not_found(
        request: Request,
        exc: OrderNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(CatalogItemNotFoundError)
    async def catalog_item_not_found(
        request: Request,
        exc: CatalogItemNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock(
        request: Request,
        exc: InsufficientStockError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidOrderError)
    async def invalid_order(
        request: Request,
        exc: InvalidOrderError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidStatusTransitionError)
    async def invalid_status_transition(
        request: Request,
        exc: InvalidStatusTransitionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ExternalServiceError)
    async def external_service_error(
        request: Request,
        exc: ExternalServiceError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": str(exc)},
        )