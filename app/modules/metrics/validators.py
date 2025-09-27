
from app.modules.metrics.constants import *
from app.shared.validators import *

def validate_weight(weight: str) -> list[str]:
    """Positive Numeric(5, 2)"""
    errors = []
    if weight:
        is_valid, error_type = validate_numeric(weight, WEIGHT_PRECISION, WEIGHT_SCALE, WEIGHT_MINIMUM, strict_min=True)
        if not is_valid:
            if error_type in [FORMAT_ERROR, SCALE_EXCEEDED, PRECISION_EXCEEDED]:
                errors.append(WEIGHT_INVALID)
            elif error_type == CONSTRAINT_VIOLATION:
                errors.append(WEIGHT_POSITIVE)
    return errors

def validate_steps(steps:str) -> list[str]:
    """Non-negative int"""
    errors = []
    if steps:
        try:
            steps_val = int(steps)
            if steps_val < 0:
                errors.append(STEPS_NEGATIVE)
        except (ValueError, TypeError):
            errors.append(STEPS_INVALID)
    return errors
def validate_calories(calories:str) -> list[str]:
    """Non-negative int"""
    errors = []
    if calories:
        try:
            cal_val = int(calories)
            if cal_val < 0:
                errors.append(CALORIES_NEGATIVE)
        except (ValueError, TypeError):
            errors.append(CALORIES_INVALID)
    return errors

# TODO: Implement wake_time + sleep_time
def validate_wake_time(wake_time:str) -> list[str]:
    errors = []

    return errors
def validate_sleep_time(sleep_time:str) -> list[str]:
    errors = []

    return errors

VALIDATION_FUNCS = {
    "weight": validate_weight,
    "steps": validate_steps,
    "wake_time": validate_wake_time,
    "sleep_time": validate_sleep_time,
    "calories": validate_calories,
}

def validate_daily_entry(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    return errors
