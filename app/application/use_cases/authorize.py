from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.errors import ErrorCode
from app.domain.entities import Event, OrderStatus, RepairOrder
from app.domain.helpers.rounding import round_amount


class AuthorizeHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id

        if order.status != OrderStatus.DIAGNOSED:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=("Transición inválida: solo se puede autorizar una orden cuando está en estado DIAGNOSED."),
                )
            )
            return

        if not order.services:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.NO_SERVICES.value,
                    message=(f"No existen servicios válidos para autorizar la orden {order_id}."),
                )
            )
            return

        subtotal: float = 0

        for svc in order.services:
            subtotal += svc.labor_estimated_cost

            if svc.components:
                for comp in svc.components:
                    subtotal += comp.estimated_cost

        authorized_amount = round_amount(subtotal * 1.16)

        order.subtotal_estimated = subtotal
        order.authorized_amount = authorized_amount
        order.authorized = True
        order.status = OrderStatus.AUTHORIZED

        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.AUTHORIZED)
        self._events_repo.append(event)
