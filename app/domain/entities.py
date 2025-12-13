from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OrderStatus(str, Enum):

    CREATED = "CREATED"
    DIAGNOSED = "DIAGNOSED"
    AUTHORIZED = "AUTHORIZED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass
class Component:
    description: str
    estimated_cost: float


@dataclass
class Service:
    index: int
    description: str
    labor_estimated_cost: float
    real_cost: float | None = None
    components: list[Component] = field(default_factory=list)
    completed: bool = False


@dataclass
class RepairOrder:
    order_id: str
    customer: str
    vehicle: str
    authorized: bool = False
    status: OrderStatus = OrderStatus.CREATED
    services: list[Service] = field(default_factory=list)
    subtotal_estimated: float = 0
    authorized_amount: float = 0
    real_total: float = 0


@dataclass
class Event:
    order_id: str
    type: OrderStatus
