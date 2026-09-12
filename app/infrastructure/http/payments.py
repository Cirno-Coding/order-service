from decimal import Decimal
from uuid import UUID

import httpx

from app.application.exceptions import ExternalServiceError
from app.application.ports.payments import PaymentsGateway


class CapashinoPaymentsClient(PaymentsGateway):
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def create_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        idempotency_key: str,
        callback_url: str,
    ) -> UUID:
        try:
            response = await self._client.post(
                f"{self._base_url}/api/payments",
                headers={"X-API-Key": self._api_key},
                json={
                    "order_id": str(order_id),
                    "amount": str(amount),
                    "callback_url": callback_url,
                    "idempotency_key": idempotency_key,
                },
            )
        except httpx.HTTPError as error:
            raise ExternalServiceError(
                "Payments Service is unavailable"
            ) from error

        if response.is_error:
            raise ExternalServiceError(
                f"Payments Service returned HTTP {response.status_code}"
            )

        return UUID(response.json()["id"])