from __future__ import annotations

from app.application.dtos import CommandDTO, ErrorViewDTO
from app.application.use_cases.base import CommandHandler
from app.domain.entities import Component, Service, OrderStatus, RepairOrder
from app.domain.errors import ErrorCode


class AddServiceHandler(CommandHandler):
    def handle(self, cmd: CommandDTO, errors: list[ErrorViewDTO]) -> None:
        order: RepairOrder | None = self._get_order_or_error(cmd, errors)
        if order is None:
            return

        order_id = order.order_id
        data = cmd.data
        service_data = data["service"]

        if order.status not in (OrderStatus.CREATED, OrderStatus.DIAGNOSED):
            errors.append(
                ErrorViewDTO(
                    op=cmd.op,
                    order_id=order_id,
                    code=ErrorCode.NOT_ALLOWED_AFTER_AUTHORIZATION.value,
                    message=(
                        "No se pueden agregar servicios en una orden que ya fue autorizada o está en un estado posterior "
                    ),
                )
            )
            return

        next_index = len(order.services) + 1
        raw_components = service_data.get("components", []) or []
        components: list[Component] = [
            Component(description=c["description"], estimated_cost=float(c["estimated_cost"])) for c in raw_components
        ]

        service = Service(
            index=next_index,
            description=service_data["description"],
            labor_estimated_cost=float(service_data["labor_estimated_cost"]),
            real_cost=None,
            components=components,
        )

        order.services.append(service)
        self._orders_repo.save(order)
