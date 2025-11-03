import regex

from datetime import datetime

from app.modules.time_tracking.constants import *
from app.shared.validators import validate_time_hhmm, validate_date_iso
from app.shared.logging_decorators import log_validator


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



VALIDATION_FUNCS = {
    "category": validate_category,
    "description": validate_description,
    "entry_date": validate_date_iso,
    "started_at": validate_time_hhmm,
    "ended_at": validate_time_hhmm,
}
@log_validator
def validate_time_entry(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate time entry data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)