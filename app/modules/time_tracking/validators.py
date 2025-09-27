
from datetime import datetime

from app.modules.time_tracking.constants import *


def validate_category(category: str) -> list[str]:
    errors = []
    if not category:
        errors.append(CATEGORY_REQUIRED)
    if category and len(category) > CATEGORY_MAX_LENGTH:
        errors.append(CATEGORY_TOO_LONG)
    return errors

def validate_description(description:str) -> list[str]:
    errors = []
    if description and len(description) > DESCRIPTION_MAX_LENGTH:
        errors.append(DESCRIPTION_LENGTH)
    return errors

def validate_duration_minutes(duration_minutes:str) -> list[str]:
    """Positive float"""
    errors = []
    if not duration_minutes:
        errors.append(DURATION_REQUIRED)
    if duration_minutes:
        try:
            duration_minutes_val = float(duration_minutes)
            if duration_minutes_val <= 0:
                errors.append(DURATION_POSITIVE)
        except (ValueError, TypeError):
            errors.append(DURATION_INVALID)
    return errors


# TODO: Add datetime validation for started_at/ended_at


VALIDATION_FUNCS = {
    "category": validate_category,
    "description": validate_description,
    "duration_minutes": validate_duration_minutes,
}

def validate_time_entry(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    return errors