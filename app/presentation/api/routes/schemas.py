from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.usecases.orders import CreateOrderUseCase, GetOrderUseCase
from app.presentation.api.dependencies import get_create_order_use_case, get_get_order_use_case
from app.presentation.api.schemas.orders import OrderCreateRequest, OrderResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    request_data: OrderCreateRequest,
    use_case: Annotated[
        CreateOrderUseCase,
        Depends(get_create_order_use_case),
    ],
) -> OrderResponse:
    order = await use_case(request_data.to_command())
    return OrderResponse.from_entity(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_order(
    order_id: UUID,
    use_case: Annotated[
        GetOrderUseCase,
        Depends(get_get_order_use_case),
    ],
) -> OrderResponse:
    order = await use_case(order_id)
    return OrderResponse.from_entity(order)