from datetime import date
from typing import Any

from app.modules.tasks import validation_constants as c
from app.modules.tasks.models import PriorityEnum
from app.shared.decorators import log_validator
from app.shared.validators import validate_date_iso, validate_enum


def validate_task_name(name: str | None) -> tuple[str | None, list[str]]:
    """Required. String, max 150 chars."""
    if not name:
        return (None, [c.TASK_NAME_REQUIRED])
    elif len(name) > c.TASK_NAME_MAX_LENGTH:
        return (None, [c.TASK_NAME_TOO_LONG])

    return (name, [])


def validate_task_priority(priority: str | None) -> tuple[Any, list[str]]:
    """
    Optional*. Valid PriorityEnum value.
    *Required if task is not a frog; must be None if it is.
    """
    if not priority:
        return (None, [])
    return validate_enum(priority, PriorityEnum, c.PRIORITY_INVALID)


def validate_due_date(due_date: str | None) -> tuple[date | None, list[str]]:
    """Optional. Datetime string (validation pending)."""
    if not due_date:
        return (None, [])

    return validate_date_iso(due_date)


TASK_VALIDATION_FUNCS = {
    "name": validate_task_name,
    "priority": validate_task_priority,
    "due_date": validate_due_date,
}


@log_validator
def validate_task(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate task data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    # Insert is_frog directly
    if data.get("is_frog") is not None:
        typed_data["is_frog"] = data.get("is_frog")

    for field, func in TASK_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    is_frog = typed_data.get("is_frog")
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


def validate_tag_name(name: str | None) -> tuple[str | None, list[str]]:
    """Required. String, max 50 chars."""
    if not name:
        return (None, [c.TAG_NAME_REQUIRED])
    if len(name) > c.TAG_NAME_MAX_LENGTH:
        return (None, [c.TAG_NAME_LENGTH])

    return (name, [])


def validate_tag_scope(scope: str | None) -> tuple[str | None, list[str]]:
    """Optional. String, max 20 chars."""
    if not scope:
        return (None, [])
    if len(scope) > c.TAG_SCOPE_MAX_LENGTH:
        return (None, [c.TAG_SCOPE_LENGTH])

    return (scope, [])


TAG_VALIDATION_FUNCS = {"name": validate_tag_name, "scope": validate_tag_scope}


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
