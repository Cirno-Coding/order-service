import httpx

from app.application.exceptions import ExternalServiceError
from app.application.ports.notifications import NotificationsGateway


class CapashinoNotificationsClient(NotificationsGateway):
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def send(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> None:
        try:
            response = await self._client.post(
                f"{self._base_url}/api/notifications",
                headers={"X-API-Key": self._api_key},
                json={
                    "message": message,
                    "reference_id": reference_id,
                    "idempotency_key": idempotency_key,
                },
            )
        except httpx.HTTPError as error:
            raise ExternalServiceError(
                "Notifications Service is unavailable"
            ) from error

        if response.is_error:
            raise ExternalServiceError(
                f"Notifications Service returned HTTP {response.status_code}"
            )