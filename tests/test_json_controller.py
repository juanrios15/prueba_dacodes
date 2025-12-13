import pytest

from app.drivers.json_controller import process_payload
from app.application.orders_service import OrderService
from app.infrastructure.in_memory_repos import InMemoryOrderRepository, InMemoryEventRepository
from app.domain.errors import ErrorCode


@pytest.fixture
def order_service() -> OrderService:
    orders_repo = InMemoryOrderRepository()
    events_repo = InMemoryEventRepository()
    return OrderService(orders_repo=orders_repo, events_repo=events_repo)


def test_process_payload_valid(order_service: OrderService):
    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T09:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T09:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {
                        "description": "Engine repair",
                        "labor_estimated_cost": "10000.00",
                        "components": [{"description": "Oil pump", "estimated_cost": "1500.00"}],
                    },
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T09:10:00Z", "data": {"order_id": "R001"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T09:11:00Z", "data": {"order_id": "R001"}},
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T09:15:00Z", "data": {"order_id": "R001"}},
            {
                "op": "SET_REAL_COST",
                "ts": "2025-03-01T09:20:00Z",
                "data": {"order_id": "R001", "service_index": 1, "real_cost": "14674.00", "completed": True},
            },
            {"op": "TRY_COMPLETE", "ts": "2025-03-01T09:25:00Z", "data": {"order_id": "R001"}},
            {"op": "DELIVER", "ts": "2025-03-01T09:30:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)
    assert "orders" in result
    assert len(result["orders"]) == 1
    assert result["orders"][0]["order_id"] == "R001"
    assert result["orders"][0]["status"] == "DELIVERED"

    assert "events" in result
    assert result["events"][-1]["type"] == "DELIVERED"
    assert result["events"][-1]["order_id"] == "R001"
    assert "errors" in result
    assert len(result["errors"]) == 0


def test_process_payload_exceeds_limit(order_service: OrderService):
    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T09:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T09:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {
                        "description": "Engine repair",
                        "labor_estimated_cost": "10000.00",
                        "components": [{"description": "Oil pump", "estimated_cost": "1500.00"}],
                    },
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T09:10:00Z", "data": {"order_id": "R001"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T09:11:00Z", "data": {"order_id": "R001"}},
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T09:15:00Z", "data": {"order_id": "R001"}},
            {
                "op": "SET_REAL_COST",
                "ts": "2025-03-01T09:20:00Z",
                "data": {"order_id": "R001", "service_index": 1, "real_cost": "15000.00", "completed": True},
            },
            {"op": "TRY_COMPLETE", "ts": "2025-03-01T09:25:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)
    assert "orders" in result
    assert result["orders"][0]["status"] == "WAITING_FOR_APPROVAL"
    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.REQUIRES_REAUTH.value
    assert result["errors"][0]["op"] == "TRY_COMPLETE"


def test_process_payload_exactly_limit(order_service: OrderService):
    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T10:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T10:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {"description": "Simple service", "labor_estimated_cost": "1000.00", "components": []},
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T10:10:00Z", "data": {"order_id": "R001"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T10:11:00Z", "data": {"order_id": "R001"}},
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T10:15:00Z", "data": {"order_id": "R001"}},
            {
                "op": "SET_REAL_COST",
                "ts": "2025-03-01T10:20:00Z",
                "data": {"order_id": "R001", "service_index": 1, "real_cost": "1276.00", "completed": True},
            },
            {"op": "TRY_COMPLETE", "ts": "2025-03-01T10:25:00Z", "data": {"order_id": "R001"}},
            {"op": "DELIVER", "ts": "2025-03-01T10:30:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)

    assert "orders" in result
    assert len(result["orders"]) == 1
    assert result["orders"][0]["order_id"] == "R001"
    assert result["orders"][0]["status"] == "DELIVERED"

    assert "events" in result
    assert result["events"][-1]["type"] == "DELIVERED"
    assert result["events"][-1]["order_id"] == "R001"
    assert "errors" in result
    assert len(result["errors"]) == 0


def test_process_payload_reauthorization(order_service: OrderService):

    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T11:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T11:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {"description": "Major service", "labor_estimated_cost": "1000.00", "components": []},
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T11:10:00Z", "data": {"order_id": "R001"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T11:11:00Z", "data": {"order_id": "R001"}},
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T11:15:00Z", "data": {"order_id": "R001"}},
            {
                "op": "SET_REAL_COST",
                "ts": "2025-03-01T11:20:00Z",
                "data": {"order_id": "R001", "service_index": 1, "real_cost": "1500.00", "completed": True},
            },
            {"op": "TRY_COMPLETE", "ts": "2025-03-01T11:25:00Z", "data": {"order_id": "R001"}},
            {
                "op": "REAUTHORIZE",
                "ts": "2025-03-01T11:30:00Z",
                "data": {"order_id": "R001", "new_authorized_amount": "2000.00"},
            },
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T11:35:00Z", "data": {"order_id": "R001"}},
            {"op": "TRY_COMPLETE", "ts": "2025-03-01T11:40:00Z", "data": {"order_id": "R001"}},
            {"op": "DELIVER", "ts": "2025-03-01T11:45:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)

    assert "orders" in result
    assert len(result["orders"]) == 1
    assert result["orders"][0]["order_id"] == "R001"
    assert result["orders"][0]["status"] == "DELIVERED"

    assert "events" in result
    assert result["events"][-1]["type"] == "DELIVERED"
    assert result["events"][-1]["order_id"] == "R001"

    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.REQUIRES_REAUTH.value
    assert result["errors"][0]["op"] == "TRY_COMPLETE"


def test_progress_without_authorization(order_service: OrderService):
    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T12:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T12:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {"description": "Basic inspection", "labor_estimated_cost": "500.00", "components": []},
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T12:10:00Z", "data": {"order_id": "R001"}},
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T12:15:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)

    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.SEQUENCE_ERROR.value


def test_process_modify_after_authorization(order_service: OrderService):

    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T13:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "ABC-123"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T13:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {"description": "Basic maintenance", "labor_estimated_cost": "500.00", "components": []},
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T13:10:00Z", "data": {"order_id": "R001"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T13:15:00Z", "data": {"order_id": "R001"}},
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T13:20:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {
                        "description": "Oil change",
                        "labor_estimated_cost": "300.00",
                        "components": [{"description": "Engine oil", "estimated_cost": "100.00"}],
                    },
                },
            },
        ]
    }

    result = process_payload(payload, order_service)

    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.NOT_ALLOWED_AFTER_AUTHORIZATION.value


def test_process_cancel_order(order_service: OrderService):

    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T14:00:00Z",
                "data": {"order_id": "R001", "customer": "ACME", "vehicle": "CAN-707"},
            },
            {
                "op": "ADD_SERVICE",
                "ts": "2025-03-01T14:05:00Z",
                "data": {
                    "order_id": "R001",
                    "service": {"description": "Pre-check", "labor_estimated_cost": "300.00", "components": []},
                },
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T14:10:00Z", "data": {"order_id": "R001"}},
            {
                "op": "CANCEL",
                "ts": "2025-03-01T14:15:00Z",
                "data": {"order_id": "R001", "reason": "Customer changed mind"},
            },
            {"op": "SET_STATE_IN_PROGRESS", "ts": "2025-03-01T12:15:00Z", "data": {"order_id": "R001"}},
        ]
    }

    result = process_payload(payload, order_service)

    assert "orders" in result
    assert result["orders"][0]["status"] == "CANCELLED"
    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.ORDER_CANCELLED.value


def test_process_no_services(order_service: OrderService):

    payload = {
        "commands": [
            {
                "op": "CREATE_ORDER",
                "ts": "2025-03-01T15:00:00Z",
                "data": {"order_id": "R008", "customer": "EMPTY_CORP", "vehicle": "NOS-808"},
            },
            {"op": "SET_STATE_DIAGNOSED", "ts": "2025-03-01T15:05:00Z", "data": {"order_id": "R008"}},
            {"op": "AUTHORIZE", "ts": "2025-03-01T15:10:00Z", "data": {"order_id": "R008"}},
        ]
    }

    result = process_payload(payload, order_service)

    assert "errors" in result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["code"] == ErrorCode.NO_SERVICES.value
