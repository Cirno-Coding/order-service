from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.orders import CreateOrderCommand
from app.domain.entities import Order, OrderStatus


class OrderCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str = Field(min_length=1, max_length=120)
    item_id: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=1000)
    idempotency_key: str = Field(min_length=1, max_length=120)

    def to_command(self) -> CreateOrderCommand:
        return CreateOrderCommand(
            user_id=self.user_id,
            item_id=str(self.item_id),
            quantity=self.quantity,
            idempotency_key=self.idempotency_key,
        )


class StatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: OrderStatus
    created_at: datetime


class OrderResponse(BaseModel):
    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    status_history: list[StatusHistoryResponse]

    @classmethod
    def from_entity(cls, order: Order) -> "OrderResponse":
        return cls(
            id=order.id,
            user_id=order.user_id,
            item_id=UUID(order.item_id),
            quantity=order.quantity,
            amount=order.amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            status_history=[
                StatusHistoryResponse(
                    status=history.status,
                    created_at=history.created_at,
                )
                for history in order.status_history
            ],
        )