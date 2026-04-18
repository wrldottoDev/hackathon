from collections.abc import Iterable
from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")
ZERO_MONEY = Decimal("0.00")


def to_money(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return ZERO_MONEY
    if isinstance(value, Decimal):
        decimal_value = value
    else:
        decimal_value = Decimal(str(value))
    return decimal_value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def sum_money(values: Iterable[Decimal | int | float | str]) -> Decimal:
    total = ZERO_MONEY
    for value in values:
        total += to_money(value)
    return to_money(total)
