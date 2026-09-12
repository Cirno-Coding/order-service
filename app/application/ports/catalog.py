from abc import ABC, abstractmethod

from app.domain.entities import CatalogItem


class CatalogGateway(ABC):
    @abstractmethod
    async def get_item(self, item_id: str) -> CatalogItem | None:
        pass