from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import RepairOrder, Event, OrderStatus
from app.domain.errors import ErrorCode


class CreateOrderHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        data: dict = cmd.data
        order_id: str = data["order_id"]
        customer: str = data["customer"]
        vehicle: str = data["vehicle"]

        existing: RepairOrder | None = self._orders_repo.get_by_id(order_id)
        if existing is not None:
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.INVALID_OPERATION.value,
                    message=f"La orden {order_id} ya existe.",
                )
            )
            return

        order: RepairOrder = RepairOrder(order_id=order_id, customer=customer, vehicle=vehicle)
        self._orders_repo.save(order)

        event: Event = Event(order_id=order_id, type=OrderStatus.CREATED)
        self._events_repo.append(event)
