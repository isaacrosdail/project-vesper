
from typing import Any

from app.modules.tasks.constants import *
from app.modules.tasks.models import PriorityEnum
from app.shared.validators import validate_enum


def validate_task_name(name: str) -> tuple[str | None, list[str]]:
    """Required. String, max 150 chars."""
    if not name:
        return (None, [TASK_NAME_REQUIRED])
    elif len(name) > TASK_NAME_MAX_LENGTH:
        return (None, [TASK_NAME_TOO_LONG])

    return (name, [])


def validate_task_priority(priority: str) -> tuple[Any, list[str]]:
    """Required. Valid PriorityEnum value."""
    return validate_enum(priority, PriorityEnum, PRIORITY_REQUIRED, PRIORITY_INVALID)


def validate_due_date(due_date: str) -> tuple[str | None, list[str]]:
    """Optional. Datetime string (validation pending)."""
    errors = []
    # TODO: Add datetime parsing validation once datetime architecture is finalized
    return (due_date, errors)


TASK_VALIDATION_FUNCS = {
    "name": validate_task_name,
    "priority": validate_task_priority,
    "due_date": validate_due_date,
}

# TODO: Validate is_frog + due_date constraint here or in service?
def validate_task(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate task data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}
    
    for field, func in TASK_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value
    
    return (typed_data, errors)




def validate_tag_name(name: str) -> tuple[str | None, list[str]]:
    """Required. String, max 50 chars."""
    if not name:
        return (None, [TAG_NAME_REQUIRED])
    if len(name) > TAG_NAME_MAX_LENGTH:
        return (None, [TAG_NAME_LENGTH])
    
    return (name, [])


def validate_tag_scope(scope: str) -> tuple[str | None, list[str]]:
    """Optional. String, max 20 chars."""
    if not scope:
        return (None, [])
    if len(scope) > TAG_SCOPE_MAX_LENGTH:
        return (None, [TAG_SCOPE_LENGTH])

    return (scope, [])


TAG_VALIDATION_FUNCS = {
    "name": validate_tag_name,
    "scope": validate_tag_scope
}

# TODO: Move elsewhere now that this is in shared/models.py?
def validate_tag(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate tag data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in TAG_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return (typed_data, errors)