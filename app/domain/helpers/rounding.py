from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_EVEN


getcontext().rounding = ROUND_HALF_EVEN


def round_amount(value) -> float:
    return float(round(Decimal(str(value)), 2))


# TODO: Aplicar esto en donde se hagan calculos de redondeo
# TODO: Agregar tests para redondeo half even
# TODO: Crear README.md
