from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import InvalidOrderError, InvalidStatusTransitionError


class OrderStatus(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class CatalogItem:
    id: str
    name: str
    price: Decimal
    available_qty: int

    def has_stock(self, quantity: int) -> bool:
        return self.available_qty >= quantity


@dataclass(frozen=True)
class OrderStatusHistory:
    status: OrderStatus
    created_at: datetime


@dataclass
class Order:
    id: UUID
    user_id: str
    item_id: str
    quantity: int
    item_price: Decimal
    amount: Decimal
    status: OrderStatus
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
    status_history: list[OrderStatusHistory]

    @classmethod
    def create(
        cls,
        user_id: str,
        item: CatalogItem,
        quantity: int,
        idempotency_key: str,
    ) -> "Order":
        if not user_id.strip():
            raise InvalidOrderError("User id must not be empty")

        if not idempotency_key.strip():
            raise InvalidOrderError("Idempotency key must not be empty")

        if quantity <= 0:
            raise InvalidOrderError("Quantity must be positive")

        if not item.has_stock(quantity):
            raise InvalidOrderError(
                f"Insufficient stock. Available: {item.available_qty}, requested: {quantity}"
            )

        now = datetime.now(UTC)
        amount = item.price * quantity

        return cls(
            id=uuid4(),
            user_id=user_id,
            item_id=item.id,
            quantity=quantity,
            item_price=item.price,
            amount=amount,
            status=OrderStatus.NEW,
            idempotency_key=idempotency_key,
            created_at=now,
            updated_at=now,
            status_history=[
                OrderStatusHistory(
                    status=OrderStatus.NEW,
                    created_at=now,
                )
            ],
        )

    def pay(self) -> None:
        self._change_status(
            expected_statuses={OrderStatus.NEW},
            new_status=OrderStatus.PAID,
        )

    def ship(self) -> None:
        self._change_status(
            expected_statuses={OrderStatus.PAID},
            new_status=OrderStatus.SHIPPED,
        )

    def cancel(self) -> None:
        self._change_status(
            expected_statuses={OrderStatus.NEW, OrderStatus.PAID},
            new_status=OrderStatus.CANCELLED,
        )

    def _change_status(
        self,
        expected_statuses: set[OrderStatus],
        new_status: OrderStatus,
    ) -> None:
        if self.status not in expected_statuses:
            raise InvalidStatusTransitionError(
                f"Cannot change order from {self.status} to {new_status}"
            )

        now = datetime.now(UTC)
        self.status = new_status
        self.updated_at = now
        self.status_history.append(
            OrderStatusHistory(
                status=new_status,
                created_at=now,
            )
        )