from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.usecases.payment_callback import (
    ProcessPaymentCallbackUseCase,
)
from app.presentation.api.dependencies import (
    get_payment_callback_use_case,
)
from app.presentation.api.schemas.orders import OrderResponse
from app.presentation.api.schemas.payments import PaymentCallbackRequest

router = APIRouter(
    prefix="/api/orders",
    tags=["payments"],
)


@router.post(
    "/payment-callback",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
async def payment_callback(
    request_data: PaymentCallbackRequest,
    use_case: Annotated[
        ProcessPaymentCallbackUseCase,
        Depends(get_payment_callback_use_case),
    ],
) -> OrderResponse:
    order = await use_case(request_data.to_command())
    return OrderResponse.from_entity(order)