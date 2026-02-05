from datetime import date
from typing import Any

from app.modules.tasks import validation_constants as c
from app.modules.tasks.models import PriorityEnum
from app.shared.decorators import log_validator
from app.shared.type_defs import ValidatorFunc
from app.shared.validators import (
    validate_date_iso,
    validate_optional_enum,
    validate_optional_string,
    validate_required_string,
)


def validate_due_date(due_date: str | None) -> tuple[date | None, list[str]]:
    """Optional. Datetime string (validation pending)."""
    if not due_date:
        return (None, [])

    return validate_date_iso(due_date)


TASK_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "name": lambda v: validate_required_string(
        v, c.TASK_NAME_MAX_LENGTH, c.TASK_NAME_REQUIRED, c.TASK_NAME_TOO_LONG
    ),
    "priority": lambda v: validate_optional_enum(
        v, PriorityEnum, c.PRIORITY_INVALID
    ),
    "due_date": validate_due_date,
}


@log_validator
def validate_task(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate task data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in TASK_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    # Insert is_frog directly
    is_frog = data.get("is_frog", False)
    typed_data['is_frog'] = is_frog

    due_date = typed_data.get("due_date")
    priority = typed_data.get("priority")

    if is_frog:
        # Frog tasks must have due_date
        if not due_date:
            errors.setdefault("due_date", []).append(c.FROG_REQUIRES_DUE_DATE)
        # Frog tasks must not have priority
        if priority is not None:
            errors.setdefault("priority", []).append(c.FROG_REQUIRES_NO_PRIORITY)
    # Non-frog tasks must have priority
    elif priority is None:
        errors.setdefault("priority", []).append(c.PRIORITY_REQUIRED_NON_FROG)

    return (typed_data, errors)


TAG_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "name": lambda v: validate_required_string(
        v, c.TAG_NAME_MAX_LENGTH, c.TAG_NAME_REQUIRED, c.TAG_NAME_LENGTH
    ),
    "scope": lambda v: validate_optional_string(
        v, c.TAG_SCOPE_MAX_LENGTH, c.TAG_SCOPE_LENGTH
    )
}


# NOTE: Move elsewhere now that this is in shared/models.py?
@log_validator
def validate_tag(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate tag data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in TAG_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)
