from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import OrderStatus, Event, RepairOrder
from app.domain.errors import ErrorCode


class DeliverHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id

        if order.status != OrderStatus.COMPLETED:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=("Transición inválida: solo se puede entregar un vehículo cuando la orden está COMPLETED."),
                )
            )
            return

        order.status = OrderStatus.DELIVERED
        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.DELIVERED)
        self._events_repo.append(event)
