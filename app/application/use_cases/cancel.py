from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import OrderStatus, Event, RepairOrder
from app.domain.errors import ErrorCode


class CancelHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id

        if order.status in (OrderStatus.COMPLETED, OrderStatus.DELIVERED):
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=("No se puede cancelar una orden que ya fue completada o entregada."),
                )
            )
            return

        order.status = OrderStatus.CANCELLED
        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.CANCELLED)
        self._events_repo.append(event)
