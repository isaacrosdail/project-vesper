
from app.modules.tasks.models import PriorityEnum

from app.modules.tasks.constants import *
from app.shared.validators import validate_enum

def validate_task_name(name: str) -> list[str]:
    errors = []
    if not name:
        errors.append(TASK_NAME_REQUIRED)
    elif len(name) > TASK_NAME_MAX_LENGTH:
        errors.append(TASK_NAME_TOO_LONG)
    return errors

def validate_task_priority(priority: str) -> list[str]:
    return validate_enum(priority, PriorityEnum, PRIORITY_REQUIRED, PRIORITY_INVALID)


def validate_due_date(due_date: str) -> list[str]:
    errors = []
    # TODO: Add datetime parsing validation once datetime architecture is finalized
    return errors

TASK_VALIDATION_FUNCS = {
    "name": validate_task_name,
    "priority": validate_task_priority,
    "due_date": validate_due_date,
}


def validate_task(data: dict) -> dict[str, list[str]]:
    errors = {}
    
    for field, func in TASK_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
    
    return errors


# TODO: Move elsewhere now that this is in shared/models.py?
def validate_tag(data: dict) -> list[str]:
    errors = []
    
    name = data.get("name")
    scope = data.get("scope")
    
    # Name: Required, max 50 chars
    if not name:
        errors.append(TAG_NAME_REQUIRED)
    if name and len(name) > TAG_NAME_MAX_LENGTH:
        errors.append(TAG_NAME_LENGTH)
    
    # Scope (optional): max 20 chars
    if scope and len(scope) > TAG_SCOPE_MAX_LENGTH:
        errors.append(TAG_SCOPE_LENGTH)
    
    return errors