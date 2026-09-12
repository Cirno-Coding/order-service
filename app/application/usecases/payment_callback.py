from app.application.dto.orders import PaymentCallbackCommand
from app.application.exceptions import OrderNotFoundError
from app.application.outbox_messages import (
    notification_message,
    order_paid_message,
)
from app.application.ports.uow import UnitOfWorkFactory
from app.domain.entities import Order
from app.domain.exceptions import InvalidOrderError


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

            if command.amount != order.amount:
                raise InvalidOrderError(
                    "Payment amount does not match order amount"
                )

            if command.status == "succeeded":
                order.pay()

                await uow.orders.update(order)

                await uow.outbox.add(
                    order_paid_message(order)
                )

                await uow.outbox.add(
                    notification_message(order)
                )

            elif command.status == "failed":
                order.cancel()

                await uow.orders.update(order)

                await uow.outbox.add(
                    notification_message(
                        order,
                        cancel_reason=(
                            command.error_message
                            or "Платёж не был обработан"
                        ),
                    )
                )

            else:
                raise InvalidOrderError(
                    f"Unsupported payment status: {command.status}"
                )

            await uow.payment_callbacks.add(
                payment_id=command.payment_id,
                order_id=command.order_id,
                status=command.status,
            )

            await uow.commit()

            return order