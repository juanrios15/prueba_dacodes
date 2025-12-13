from datetime import datetime

from pydantic import BaseModel


class CommandDTO(BaseModel):
    op: str
    ts: datetime
    data: dict


class OrderViewDTO(BaseModel):
    order_id: str
    status: str
    customer: str
    vehicle: str
    subtotal_estimated: float
    authorized_amount: float | None = None
    real_total: float | None = None


class EventViewDTO(BaseModel):
    order_id: str
    type: str


class ErrorViewDTO(BaseModel):
    op: str
    order_id: str
    code: str
    message: str


class ResultDTO(BaseModel):
    orders: list[OrderViewDTO] = []
    events: list[EventViewDTO] = []
    errors: list[ErrorViewDTO] = []
