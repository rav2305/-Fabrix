from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .exceptions import ValidationError


TWOPLACES = Decimal("0.01")


def parse_decimal(value, field_name):
    try:
        return quantize_money(Decimal(str(value if value is not None else 0)))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid numeric value for {field_name}") from exc


def parse_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid integer value for {field_name}") from exc
    return parsed


def quantize_money(value):
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
