from uuid import UUID

from app.application.dto.orders import CreateOrderCommand
from app.application.exceptions import CatalogItemNotFoundError, InsufficientStockError, OrderNotFoundError
from app.application.ports.catalog import CatalogGateway
from app.application.ports.uow import UnitOfWorkFactory
from app.domain.entities import Order


class CreateOrderUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        catalog_gateway: CatalogGateway,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog_gateway = catalog_gateway

    async def __call__(self, command: CreateOrderCommand) -> Order:
        async with self._uow_factory() as uow:
            existing_order = await uow.orders.get_by_idempotency_key(
                command.idempotency_key
            )

        if existing_order is not None:
            return existing_order

        item = await self._catalog_gateway.get_item(command.item_id)

        if item is None:
            raise CatalogItemNotFoundError(
                f"Catalog item {command.item_id} not found"
            )

        if not item.has_stock(command.quantity):
            raise InsufficientStockError(
                f"Not enough stock for item {item.id}"
            )

        order = Order.create(
            user_id=command.user_id,
            item=item,
            quantity=command.quantity,
            idempotency_key=command.idempotency_key,
        )

        async with self._uow_factory() as uow:
            await uow.orders.add(order)
            await uow.commit()

        return order


class GetOrderUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, order_id: UUID) -> Order:
        async with self._uow_factory() as uow:
            order = await uow.orders.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        return order