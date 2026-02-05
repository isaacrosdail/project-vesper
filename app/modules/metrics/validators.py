from datetime import date, datetime
from typing import Any

from app.modules.metrics import validation_constants as c
from app.shared.decorators import log_validator
from app.shared.type_defs import ValidatorFunc
from app.shared.validators import (
    validate_date_iso,
    validate_optional_int,
    validate_time_hhmm,
)


def validate_entry_date(entry_date_str: str | None) -> tuple[date | None, list[str]]:
    """Required. Date string in YYYY-MM-DD format."""
    if not entry_date_str:
        return (None, ["Entry date is required"])

    return validate_date_iso(entry_date_str)

def validate_datetime_local(dt_str: str | None) -> tuple[datetime | None, list[str]]:
    """Parse datetime-local string (YYYY-MM-DDTHH:MM) return naive datetime."""
    if not dt_str:
        return (None, [])

    try:
        return (datetime.fromisoformat(dt_str), [])
    except ValueError:
        return (None, ["Invalid datetime format"])

def validate_weight(weight: str | None) -> tuple[float | None, list[str]]:
    """Positive float"""

    if not weight:
        return (None, [])

    try:
        weight_float = float(weight)
        if weight_float < 0:
            return (None, [c.WEIGHT_POSITIVE])
    except ValueError:
        return (None, [c.WEIGHT_INVALID])

    return (weight_float, [])


def validate_time_hhmm_format(time_str: str | None) -> tuple[str | None, list[str]]:
    """Optional. Time string in HH:MM format."""
    if not time_str:
        return (None, [])

    return validate_time_hhmm(time_str)


VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "entry_date": validate_entry_date,
    "weight": validate_weight,
    "steps": lambda v: validate_optional_int(
        v, c.STEPS_INVALID
    ),
    "wake_datetime": validate_datetime_local,
    "sleep_datetime": validate_datetime_local,
    "calories": lambda v: validate_optional_int(
        v, c.CALORIES_INVALID
    ),
}


@log_validator
def validate_daily_entry(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    typed_data = {}
    errors: dict[str, list[str]] = {}

    if data.get("weight") and not data.get("weight_units"):
        errors["weight_units"] = ["Weight units required"]

    elif data.get("weight_units") and data.get("weight_units") not in {"kg", "lbs"}:
        errors["weight_units"] = ["Must be in 'kg' or 'lbs'"]
    # weight_units is valid -> add to typed_data
    elif data.get("weight"):
        typed_data["weight_units"] = data["weight_units"]

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)

        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return typed_data, errors
