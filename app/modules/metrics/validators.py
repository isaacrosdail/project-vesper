
from app.modules.metrics.constants import *
from app.shared.validators import *


def validate_weight(weight: str) -> tuple[float | None, list[str]]:
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


def validate_steps(steps:str) -> tuple[int | None, list[str]]:
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


def validate_calories(calories:str) -> tuple[int | None, list[str]]:
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


def validate_time_hhmm_format(time_str: str) -> tuple[str | None, list[str]]:
    """Optional. Time string in HH:MM format."""
    if not time_str:
        return (None, [])

    return validate_time_hhmm(time_str)


VALIDATION_FUNCS = {
    "weight": validate_weight,
    "steps": validate_steps,
    "wake_time": validate_time_hhmm_format,
    "sleep_time": validate_time_hhmm_format,
    "calories": validate_calories,
}

def validate_daily_entry(data: dict) -> tuple[dict, dict[str, list[str]]]:
    typed_data = {}
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value) # unpack tuple

        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None: # only store if no errors for given field?
            typed_data[field] = typed_value

    return typed_data, errors
