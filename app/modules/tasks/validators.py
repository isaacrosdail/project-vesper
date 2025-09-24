
from app.modules.tasks.models import Priority


# Task constants
TASK_NAME_REQUIRED = "Task name is required"
TASK_NAME_LENGTH = "Task name must be under 255 characters"
PRIORITY_INVALID = "Invalid priority"
DUE_DATE_INVALID = "Due date must be a valid datetime"

# Tag constants  
TAG_NAME_REQUIRED = "Tag name is required"
TAG_NAME_LENGTH = "Tag name must be under 50 characters"
TAG_SCOPE_LENGTH = "Tag scope must be under 20 characters"


def validate_task(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    name = data.get("name", "").strip()
    priority = data.get("priority", "").strip()
    due_date = data.get("due_date", "")
    
    # Name: Required, max 255 chars
    if not name:
        errors.append(TASK_NAME_REQUIRED)
    if name and len(name) > 255:
        errors.append(TASK_NAME_LENGTH)
    
    # Priority (optional): Valid enum
    if priority:
        valid_priorities = [p.value for p in Priority]
        if priority not in valid_priorities:
            errors.append(PRIORITY_INVALID)
    
    # TODO: Add datetime parsing for due_date
    # Due_date (optional): Valid datetime format
    
    return errors

def validate_tag(data: dict) -> list[str]:
    errors = []
    
    name = data.get("name", "").strip()
    scope = data.get("scope", "").strip()
    
    # Name: Required, max 50 chars
    if not name:
        errors.append(TAG_NAME_REQUIRED)
    if name and len(name) > 50:
        errors.append(TAG_NAME_LENGTH)
    
    # Scope (optional): max 20 chars
    if scope and len(scope) > 20:
        errors.append(TAG_SCOPE_LENGTH)
    
    return errors