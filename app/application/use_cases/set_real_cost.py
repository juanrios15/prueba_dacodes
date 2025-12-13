from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.errors import ErrorCode
from app.domain.entities import RepairOrder
from app.domain.helpers.rounding import round_amount


class SetRealCostHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        data = cmd.data
        order_id = order.order_id

        try:
            service_index = int(data["service_index"])
            real_cost_str = data.get("real_cost")
        except (KeyError, ValueError):
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.INVALID_OPERATION.value,
                    message="Los campos 'service_index' y 'real_cost' son obligatorios.",
                )
            )
            return

        real_cost: float = round_amount(real_cost_str)
        completed: bool = bool(data.get("completed", False))

        service_pos = service_index - 1
        service = order.services[service_pos]

        service.real_cost = real_cost
        service.completed = completed
        self._orders_repo.save(order)
