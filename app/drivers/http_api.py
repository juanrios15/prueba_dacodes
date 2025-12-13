# app/drivers/http_api.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.orders_service import OrderService
from app.drivers.json_controller import process_payload
from app.infrastructure.in_memory_repos import InMemoryOrderRepository, InMemoryEventRepository

router = APIRouter()


def get_order_service() -> OrderService:
    orders_repo = InMemoryOrderRepository()
    events_repo = InMemoryEventRepository()
    return OrderService(orders_repo=orders_repo, events_repo=events_repo)


@router.post("/process-orders/")
def process_repair_orders(payload: dict, service: OrderService = Depends(get_order_service)) -> dict:
    return process_payload(payload, service)
