from __future__ import annotations

from .dtos import CommandDTO, ErrorViewDTO, EventViewDTO, OrderViewDTO, ResultDTO
from app.application.use_cases.create_order import CreateOrderHandler
from app.application.use_cases.add_service import AddServiceHandler
from app.application.use_cases.set_state_diagnosed import SetStateDiagnosedHandler
from app.application.use_cases.authorize import AuthorizeHandler
from app.application.use_cases.set_state_in_progress import SetStateInProgressHandler
from app.application.use_cases.set_real_cost import SetRealCostHandler
from app.application.use_cases.try_complete import TryCompleteHandler
from app.application.use_cases.reauthorize import ReauthorizeHandler
from app.application.use_cases.deliver import DeliverHandler
from app.application.use_cases.cancel import CancelHandler
from app.domain.errors import ErrorCode
from app.domain.entities import OrderStatus
from app.domain.ports import OrderRepositoryPort, EventRepositoryPort


class OrderService:
    def __init__(self, orders_repo: OrderRepositoryPort, events_repo: EventRepositoryPort) -> None:
        self._orders_repo = orders_repo
        self._events_repo = events_repo
        self._errors: list[ErrorViewDTO] = []

        self._handlers: dict = {
            "CREATE_ORDER": CreateOrderHandler(orders_repo, events_repo),
            "ADD_SERVICE": AddServiceHandler(orders_repo, events_repo),
            "SET_STATE_DIAGNOSED": SetStateDiagnosedHandler(orders_repo, events_repo),
            "AUTHORIZE": AuthorizeHandler(orders_repo, events_repo),
            "SET_STATE_IN_PROGRESS": SetStateInProgressHandler(orders_repo, events_repo),
            "SET_REAL_COST": SetRealCostHandler(orders_repo, events_repo),
            "TRY_COMPLETE": TryCompleteHandler(orders_repo, events_repo),
            "REAUTHORIZE": ReauthorizeHandler(orders_repo, events_repo),
            "DELIVER": DeliverHandler(orders_repo, events_repo),
            "CANCEL": CancelHandler(orders_repo, events_repo),
        }

    def execute(self, commands: list[CommandDTO]) -> ResultDTO:
        """
        Execute repair order commands and build a response view.

        Args:
            commands: Ordered list of command DTOs to be processed in sequence.

        Returns:
            ResultDTO: Response view with orders, events and errors.
        """
        order_ids: set[str] = set()
        for cmd in commands:
            handler = self._handlers.get(cmd.op)
            order_id: str = cmd.data.get("order_id", "")
            if order_id:
                order_ids.add(order_id)
            if handler is None:
                self._errors.append(
                    ErrorViewDTO(
                        op=cmd.op,
                        order_id=order_id,
                        code=ErrorCode.INVALID_OPERATION.value,
                        message=f"Operación desconocida: {cmd.op}",
                    )
                )
                continue

            handler.handle(cmd, self._errors)
        order_views: list[OrderViewDTO] = []
        for order in order_ids:
            order = self._orders_repo.get_by_id(order_id)
            if not order:
                continue
            order_views.append(
                OrderViewDTO(
                    order_id=order.order_id,
                    status=order.status.value,
                    customer=order.customer,
                    vehicle=order.vehicle,
                    subtotal_estimated=order.subtotal_estimated,
                    authorized_amount=order.authorized_amount,
                    real_total=order.real_total,
                )
            )
        event_views: list[EventViewDTO] = []
        for event in self._events_repo.get_all():
            if event.order_id in order_ids:
                event_views.append(EventViewDTO(order_id=event.order_id, type=event.type.value))
        return ResultDTO(orders=order_views, events=event_views, errors=self._errors)
