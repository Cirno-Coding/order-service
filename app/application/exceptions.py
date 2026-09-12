from uuid import UUID


class OrderNotFoundError(Exception):
    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Order {order_id} not found")
        self.order_id = order_id


class CatalogItemNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class ExternalServiceError(Exception):
    pass