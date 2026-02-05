from typing import Any

from app.modules.time_tracking.validation_constants import (
    CATEGORY_MAX_LENGTH,
    CATEGORY_REQUIRED,
    CATEGORY_TOO_LONG,
    DESCRIPTION_LENGTH,
    DESCRIPTION_MAX_LENGTH,
)
from app.shared.decorators import log_validator
from app.shared.validators import (
    validate_date_iso, validate_time_hhmm, validate_optional_string, validate_required_string
)


VALIDATION_FUNCS = {
    "category": lambda v: validate_required_string(
        v, CATEGORY_MAX_LENGTH, CATEGORY_REQUIRED, CATEGORY_TOO_LONG
    ),
    "description": lambda v: validate_optional_string(
        v, DESCRIPTION_MAX_LENGTH, DESCRIPTION_LENGTH
    ),
    "entry_date": validate_date_iso,
    "started_at": validate_time_hhmm,
    "ended_at": validate_time_hhmm,
}


@log_validator
def validate_time_entry(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
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
