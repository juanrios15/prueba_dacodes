from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import OrderStatus, Event, RepairOrder
from app.domain.errors import ErrorCode
from app.domain.helpers.rounding import round_amount

class TryCompleteHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id
        if order.status != OrderStatus.IN_PROGRESS:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=(
                        "Transición inválida: solo se puede intentar completar una orden cuando está en estado IN_PROGRESS."
                    ),
                )
            )
            return

        if not order.authorized or order.authorized_amount is None:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.SEQUENCE_ERROR.value,
                    message=("No se puede completar una orden sin autorización válida."),
                )
            )
            return

        for svc in order.services:
            if not svc.completed or svc.real_cost is None:
                errors.append(
                    ErrorViewDTO(
                        op=cmd.op,
                        order_id=order_id,
                        code=ErrorCode.SEQUENCE_ERROR.value,
                        message=(
                            "No se puede completar la orden; existen servicios no completados o sin costo real asignado."
                        ),
                    )
                )
                return

        real_total = sum(svc.real_cost for svc in order.services if svc.real_cost is not None)
        order.real_total = real_total
        limit: float = round_amount(order.authorized_amount * 1.10)

        if real_total > limit:
            order.status = OrderStatus.WAITING_FOR_APPROVAL
            self._orders_repo.save(order)

            event = Event(order_id=order_id, type=OrderStatus.WAITING_FOR_APPROVAL)
            self._events_repo.append(event)

            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.REQUIRES_REAUTH.value,
                    message=(
                        f"El costo real ({real_total:.2f}) excede el 110% del monto autorizado ({order.authorized_amount:.2f}). "
                        f"Límite: {limit:.2f}."
                    ),
                )
            )
            return

        order.status = OrderStatus.COMPLETED
        self._orders_repo.save(order)

        event = Event(order_id=order_id, type=OrderStatus.COMPLETED)
        self._events_repo.append(event)
