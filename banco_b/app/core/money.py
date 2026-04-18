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
