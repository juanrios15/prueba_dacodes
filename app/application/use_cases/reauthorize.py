from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import OrderStatus, Event, RepairOrder
from app.domain.errors import ErrorCode
from app.domain.helpers.rounding import round_amount

class ReauthorizeHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id
        data = cmd.data

        if order.status != OrderStatus.WAITING_FOR_APPROVAL:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=(
                        "Transición inválida: solo se puede re-autorizar una orden en estado WAITING_FOR_APPROVAL."
                    ),
                )
            )
            return

        new_amount_str = data.get("new_authorized_amount")
        if new_amount_str is None:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.INVALID_OPERATION.value,
                    message="El campo 'new_authorized_amount' es obligatorio en REAUTHORIZE.",
                )
            )
            return

        new_amount: float = round_amount(new_amount_str)

        order.authorized_amount = new_amount
        order.authorized = True
        order.status = OrderStatus.AUTHORIZED

        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.AUTHORIZED)
        self._events_repo.append(event)
