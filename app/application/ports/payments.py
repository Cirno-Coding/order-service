from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID


class PaymentsGateway(ABC):
    @abstractmethod
    async def create_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        idempotency_key: str,
        callback_url: str,
    ) -> UUID:
        pass