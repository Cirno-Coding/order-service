from typing import Annotated, cast

from fastapi import Depends, Request

from app.application.ports.catalog import CatalogGateway
from app.application.ports.uow import UnitOfWorkFactory
from app.application.usecases.orders import CreateOrderUseCase, GetOrderUseCase


def get_uow_factory(request: Request) -> UnitOfWorkFactory:
    return cast(UnitOfWorkFactory, request.app.state.uow_factory)


def get_catalog_gateway(request: Request) -> CatalogGateway:
    return cast(CatalogGateway, request.app.state.catalog_gateway)


def get_create_order_use_case(
    uow_factory: Annotated[UnitOfWorkFactory, Depends(get_uow_factory)],
    catalog_gateway: Annotated[CatalogGateway, Depends(get_catalog_gateway)],
) -> CreateOrderUseCase:
    return CreateOrderUseCase(uow_factory, catalog_gateway)


def get_get_order_use_case(
    uow_factory: Annotated[UnitOfWorkFactory, Depends(get_uow_factory)],
) -> GetOrderUseCase:
    return GetOrderUseCase(uow_factory)