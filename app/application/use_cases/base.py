from __future__ import annotations

from abc import ABC, abstractmethod

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.domain.ports import OrderRepositoryPort, EventRepositoryPort
from app.domain.entities import OrderStatus, RepairOrder
from app.domain.errors import ErrorCode


class CommandHandler(ABC):
    def __init__(self, orders_repo: OrderRepositoryPort, events_repo: EventRepositoryPort) -> None:
        self._orders_repo = orders_repo
        self._events_repo = events_repo

    @abstractmethod
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None: ...

    def _get_order_or_error(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> RepairOrder | None:
        order_id: str = cmd.data.get("order_id")
        if not order_id:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id="",
                    code=ErrorCode.INVALID_OPERATION.value,
                    message="Falta 'order_id' en los datos del comando.",
                )
            )
            return None

        order: RepairOrder = self._orders_repo.get_by_id(order_id)
        if order is None:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.INVALID_OPERATION.value,
                    message=f"La orden {order_id} no existe.",
                )
            )
            return None

        if order and order.status == OrderStatus.CANCELLED:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.ORDER_CANCELLED.value,
                    message=(f"La orden {order_id} está CANCELLED."),
                )
            )
            return None
        return order
