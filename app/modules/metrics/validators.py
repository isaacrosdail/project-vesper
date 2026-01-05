
from datetime import date
from typing import Any

from app.modules.metrics.constants import *
from app.shared.decorators import log_validator
from app.shared.validators import *


def validate_entry_date(entry_date_str: str | None) -> tuple[date | None, list[str]]:
    """Required. Date string in YYYY-MM-DD format."""
    if not entry_date_str:
        return (None, ["Entry date is required"])
    
    return validate_date_iso(entry_date_str)


def validate_weight(weight: str | None) -> tuple[float | None, list[str]]:
    """Positive Numeric(5, 2)"""

    if not weight:
        return (None, [])

    is_valid, error_type = validate_numeric(weight, WEIGHT_PRECISION, WEIGHT_SCALE, WEIGHT_MINIMUM, strict_min=True)
    if not is_valid:
        errors = []
        if error_type in [FORMAT_ERROR, SCALE_EXCEEDED, PRECISION_EXCEEDED]:
            errors.append(WEIGHT_INVALID)
        elif error_type == CONSTRAINT_VIOLATION:
            errors.append(WEIGHT_POSITIVE)
        return (None, errors) # had errors -> no typed value

    typed_weight = float(weight)
    return (typed_weight, [])


def validate_steps(steps: str | None) -> tuple[int | None, list[str]]:
    """Non-negative int"""

    if not steps:
        return (None, [])
    
    errors = []
    try:
        steps_int = int(steps)
        if steps_int < 0:
            errors.append(STEPS_NEGATIVE)
            return (None, errors)
    except ValueError:
        errors.append(STEPS_INVALID)
        return (None, errors)

    return (steps_int, [])


def validate_calories(calories:str | None) -> tuple[int | None, list[str]]:
    """Non-negative int"""

    if not calories:
        return (None, [])
    
    errors = []
    try:
        calories_int = int(calories)
        if calories_int < 0:
            errors.append(CALORIES_NEGATIVE)
            return (None, errors)
    except (ValueError, TypeError):
        errors.append(CALORIES_INVALID)
        return (None, errors)

    return (calories_int, [])


def validate_time_hhmm_format(time_str: str | None) -> tuple[str | None, list[str]]:
    """Optional. Time string in HH:MM format."""
    if not time_str:
        return (None, [])

    return validate_time_hhmm(time_str)


VALIDATION_FUNCS = {
    "entry_date": validate_entry_date,
    "weight": validate_weight,
    "steps": validate_steps,
    "wake_time": validate_time_hhmm_format,
    "sleep_time": validate_time_hhmm_format,
    "calories": validate_calories,
}
@log_validator
def validate_daily_entry(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    typed_data = {}
    errors: dict[str, list[str]] = {}

    if data.get("weight") and not data.get("weight_units"):
        errors["weight_units"] = ["Weight units required"]

    elif data.get("weight_units") and data.get("weight_units") not in ["kg", "lbs"]:
        errors["weight_units"] = ["Must be in 'kg' or 'lbs'"]
    else:
        # weight_units is valid -> add to typed_data
        if data.get("weight"):
            typed_data["weight_units"] = data["weight_units"]

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value) # unpack tuple

        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None: # only store if no errors for given field?
            typed_data[field] = typed_value

    return typed_data, errors
