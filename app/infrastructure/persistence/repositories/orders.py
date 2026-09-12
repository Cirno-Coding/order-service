from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.ports.repositories import OrderRepository
from app.domain.entities import Order, OrderStatus, OrderStatusHistory
from app.infrastructure.persistence.models.orders import OrderModel, OrderStatusModel


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> None:
        self._session.add(self._to_model(order))

    async def get_by_id(self, order_id: UUID) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.status_history))
        )

        model = await self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_id_for_update(self, order_id: UUID) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.status_history))
            .with_for_update()
        )

        model = await self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.idempotency_key == idempotency_key)
            .options(selectinload(OrderModel.status_history))
        )

        model = await self._session.scalar(statement)

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, order: Order) -> None:
        model = await self._session.get(OrderModel, order.id)

        if model is None:
            raise RuntimeError(f"Order {order.id} does not exist")

        model.status = order.status.value
        model.updated_at = order.updated_at

        model.status_history = [
            OrderStatusModel(
                status=history.status.value,
                created_at=history.created_at,
            )
            for history in order.status_history
        ]

    @staticmethod
    def _to_model(order: Order) -> OrderModel:
        return OrderModel(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            item_price=order.item_price,
            amount=order.amount,
            status=order.status.value,
            idempotency_key=order.idempotency_key,
            created_at=order.created_at,
            updated_at=order.updated_at,
            status_history=[
                OrderStatusModel(
                    status=history.status.value,
                    created_at=history.created_at,
                )
                for history in order.status_history
            ],
        )

    @staticmethod
    def _to_entity(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            item_id=model.item_id,
            quantity=model.quantity,
            item_price=model.item_price,
            amount=model.amount,
            status=OrderStatus(model.status),
            idempotency_key=model.idempotency_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status_history=[
                OrderStatusHistory(
                    status=OrderStatus(history.status),
                    created_at=history.created_at,
                )
                for history in model.status_history
            ],
        )