from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: str
    item_id: str
    quantity: int
    idempotency_key: str


@dataclass(frozen=True)
class PaymentCallbackCommand:
    payment_id: UUID
    order_id: UUID
    status: str
    amount: Decimal
    error_message: str | None