from app.domain.entities import OrderStatus


def notification_text(
    status: OrderStatus,
    cancel_reason: str | None = None,
) -> str:
    messages = {
        OrderStatus.NEW: (
            "NEW: Ваш заказ создан и ожидает оплаты"
        ),
        OrderStatus.PAID: (
            "PAID: Ваш заказ успешно оплачен и готов к отправке"
        ),
        OrderStatus.SHIPPED: (
            "SHIPPED: Ваш заказ отправлен в доставку"
        ),
    }

    if status == OrderStatus.CANCELLED:
        reason = cancel_reason or "Причина не указана"
        return f"CANCELLED: Ваш заказ отменён. Причина: {reason}"

    return messages[status]