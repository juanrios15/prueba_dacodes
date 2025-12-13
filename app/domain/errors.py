from dataclasses import dataclass
from enum import Enum


class ErrorCode(str, Enum):
    NO_SERVICES = "NO_SERVICES"
    NOT_ALLOWED_AFTER_AUTHORIZATION = "NOT_ALLOWED_AFTER_AUTHORIZATION"
    SEQUENCE_ERROR = "SEQUENCE_ERROR"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    REQUIRES_REAUTH = "REQUIRES_REAUTH"
    INVALID_OPERATION = "INVALID_OPERATION"


@dataclass
class DomainError(Exception):
    code: ErrorCode
    message: str
    order_id: str | None = None

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"
