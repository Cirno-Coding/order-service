from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.application.dto.orders import PaymentCallbackCommand


class PaymentCallbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: UUID
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