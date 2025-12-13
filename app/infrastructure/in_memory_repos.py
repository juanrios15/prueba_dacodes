from __future__ import annotations

from app.domain.entities import Event, RepairOrder
from app.domain.ports import EventRepositoryPort, OrderRepositoryPort


class InMemoryOrderRepository(OrderRepositoryPort):
    def __init__(self) -> None:
        self._orders: dict = {}

    def get_by_id(self, order_id: str) -> RepairOrder | None:
        return self._orders.get(order_id)

    def save(self, order: RepairOrder) -> RepairOrder:
        self._orders[order.order_id] = order
        return order


class InMemoryEventRepository(EventRepositoryPort):
    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> None:
        self._events.append(event)

    def get_by_order_id(self, order_id: str) -> list[Event]:
        return [e for e in self._events if e["order_id"] == order_id]

    def get_all(self) -> list[Event]:
        return self._events
