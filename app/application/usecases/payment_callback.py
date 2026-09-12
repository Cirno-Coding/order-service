from datetime import datetime, UTC
from uuid import uuid4

from app.application.dto.events import OutboxMessage
from app.application.dto.orders import PaymentCallbackCommand
from app.application.exceptions import OrderNotFoundError
from app.application.ports.uow import UnitOfWorkFactory
from app.domain.entities import Order


class ProcessPaymentCallbackUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(
        self,
        command: PaymentCallbackCommand,
    ) -> Order:
        async with self._uow_factory() as uow:
            if await uow.payment_callbacks.exists(command.payment_id):
                order = await uow.orders.get_by_id(command.order_id)

                if order is None:
                    raise OrderNotFoundError(command.order_id)

                return order

            order = await uow.orders.get_by_id_for_update(
                command.order_id
            )

            if order is None:
                raise OrderNotFoundError(command.order_id)

            if command.status == "succeeded":
                order.pay()
            elif command.status == "failed":
                order.cancel()
            else:
                raise ValueError(
                    f"Unsupported payment status: {command.status}"
                )

            await uow.orders.update(order)

            if order.status.value == "PAID":
                await uow.outbox.add(
                    OutboxMessage(
                        id=uuid4(),
                        channel="KAFKA",
                        event_type="order.paid",
                        idempotency_key=f"order-paid:{order.id}",
                        created_at=datetime.now(UTC),
                        payload={
                            "event_type": "order.paid",
                            "order_id": str(order.id),
                            "item_id": order.item_id,
                            "quantity": order.quantity,
                            "idempotency_key": order.idempotency_key,
                        },
                    )
                )

            await uow.payment_callbacks.add(
                payment_id=command.payment_id,
                order_id=command.order_id,
                status=command.status,
            )

            await uow.commit()

            return order