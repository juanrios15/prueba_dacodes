from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Event, RepairOrder


class OrderRepositoryPort(ABC):

    @abstractmethod
    def get_by_id(self, order_id: str) -> RepairOrder | None:
        raise NotImplementedError

    @abstractmethod
    def save(self, order: RepairOrder) -> RepairOrder:
        raise NotImplementedError


class EventRepositoryPort(ABC):

    @abstractmethod
    def append(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_order_id(self, order_id: str) -> list[Event]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[Event]:
        raise NotImplementedError