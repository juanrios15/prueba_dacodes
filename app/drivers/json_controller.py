# src/repair_orders/drivers/json_controller.py
from __future__ import annotations

from app.application.dtos import CommandDTO, ResultDTO
from app.application.orders_service import OrderService


def process_payload(payload: dict, service: OrderService) -> dict:
    raw_commands: list = payload.get("commands", [])

    commands: list[CommandDTO] = []
    for item in raw_commands:
        command = CommandDTO(op=item["op"], ts=item["ts"], data=item.get("data", {}))
        commands.append(command)

    result: ResultDTO = service.execute(commands)
    return result.model_dump()
