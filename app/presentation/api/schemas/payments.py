from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from app.application.dto.orders import PaymentCallbackCommand


class PaymentCallbackRequest(BaseModel):
    # Реальный Payments Service может передать дополнительные поля
    # (например, user_id, idempotency_key, created_at).
    model_config = ConfigDict(extra="ignore")

    # Поддерживаем формат из задания (payment_id) и возможный формат
    # полного объекта платежа (id).
    payment_id: UUID = Field(
        validation_alias=AliasChoices("payment_id", "id")
    )
    order_id: UUID
    status: Literal["succeeded", "failed"]
    amount: Decimal
    error_message: str | None = None

    def to_command(self) -> PaymentCallbackCommand:
        return PaymentCallbackCommand(
            payment_id=self.payment_id,
            order_id=self.order_id,
            status=self.status,
            amount=self.amount,
            error_message=self.error_message,
        )