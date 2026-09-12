from typing import Annotated, cast

from fastapi import Depends, Request

from app.application.ports.catalog import CatalogGateway
from app.application.ports.payments import PaymentsGateway
from app.application.ports.uow import UnitOfWorkFactory
from app.application.usecases.orders import CreateOrderUseCase, GetOrderUseCase
from app.application.usecases.payment_callback import ProcessPaymentCallbackUseCase


def get_uow_factory(request: Request) -> UnitOfWorkFactory:
    return cast(UnitOfWorkFactory, request.app.state.uow_factory)


def get_catalog_gateway(request: Request) -> CatalogGateway:
    return cast(CatalogGateway, request.app.state.catalog_gateway)


def get_payments_gateway(request: Request) -> PaymentsGateway:
    return cast(PaymentsGateway, request.app.state.payments_gateway)


def get_create_order_use_case(
    request: Request,
    uow_factory: Annotated[UnitOfWorkFactory, Depends(get_uow_factory)],
    catalog_gateway: Annotated[CatalogGateway, Depends(get_catalog_gateway)],
    payments_gateway: Annotated[
        PaymentsGateway,
        Depends(get_payments_gateway),
    ],
) -> CreateOrderUseCase:
    return CreateOrderUseCase(
        uow_factory=uow_factory,
        catalog_gateway=catalog_gateway,
        payments_gateway=payments_gateway,
        payment_callback_url=request.app.state.settings.payment_callback_url,
    )


def get_get_order_use_case(
    uow_factory: Annotated[UnitOfWorkFactory, Depends(get_uow_factory)],
) -> GetOrderUseCase:
    return GetOrderUseCase(uow_factory)


def get_payment_callback_use_case(
    uow_factory: Annotated[UnitOfWorkFactory, Depends(get_uow_factory)],
) -> ProcessPaymentCallbackUseCase:
    return ProcessPaymentCallbackUseCase(uow_factory)