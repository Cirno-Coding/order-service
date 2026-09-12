from decimal import Decimal

import httpx

from app.application.exceptions import ExternalServiceError
from app.application.ports.catalog import CatalogGateway
from app.domain.entities import CatalogItem


class CapashinoCatalogClient(CatalogGateway):
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def get_item(self, item_id: str) -> CatalogItem | None:
        try:
            response = await self._client.get(
                f"{self._base_url}/api/catalog/items/{item_id}",
                headers={"X-API-Key": self._api_key},
            )
        except httpx.HTTPError as error:
            raise ExternalServiceError("Catalog Service is unavailable") from error

        if response.status_code == 404:
            return None

        if response.is_error:
            raise ExternalServiceError(
                f"Catalog Service returned HTTP {response.status_code}"
            )

        data = response.json()

        return CatalogItem(
            id=data["id"],
            name=data["name"],
            price=Decimal(data["price"]),
            available_qty=data["available_qty"],
        )