from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_EVEN


getcontext().rounding = ROUND_HALF_EVEN


def round_amount(value) -> float:
    return float(round(Decimal(str(value)), 2))
