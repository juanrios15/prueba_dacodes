from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import OrderStatus, Event, RepairOrder
from app.domain.errors import ErrorCode


class SetStateInProgressHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None  = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id

        if order.status != OrderStatus.AUTHORIZED or not order.authorized:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=("Transición inválida: solo se puede pasar a IN_PROGRESS desde una orden autorizada."),
                )
            )
            return

        order.status = OrderStatus.IN_PROGRESS
        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.IN_PROGRESS)
        self._events_repo.append(event)
