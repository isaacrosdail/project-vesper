import regex

from datetime import datetime

from app.modules.time_tracking.constants import *
from app.shared.validators import validate_time_hhmm


def validate_category(category: str) -> tuple[str | None, list[str]]:
    """Required. String, max 50 chars."""
    if not category:
        return (None, [CATEGORY_REQUIRED])
    if len(category) > CATEGORY_MAX_LENGTH:
        return (None, [CATEGORY_TOO_LONG])

    return (category, [])


def validate_description(description: str) -> tuple[str | None, list[str]]:
    """Optional. String, max 200 chars."""
    if not description:
        return (None, [])
    if len(description) > DESCRIPTION_MAX_LENGTH:
        return (None, [DESCRIPTION_LENGTH])

    return (description, [])


def validate_duration_minutes(duration_minutes: str) -> tuple[int | None, list[str]]:
    """Required. Positive integer."""
    if not duration_minutes:
        return (None, [DURATION_REQUIRED])

    try:
        duration_minutes_int = int(duration_minutes)
        if duration_minutes_int <= 0:
            return (None, [DURATION_POSITIVE])
    except (ValueError, TypeError):
        return (None, [DURATION_INVALID])
    
    return (duration_minutes_int, [])


VALIDATION_FUNCS = {
    "category": validate_category,
    "description": validate_description,
    "started_at": validate_time_hhmm,
    "duration_minutes": validate_duration_minutes,
}

def validate_time_entry(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate time entry data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return (typed_data, errors)