from app.modules.tasks.models import Priority

def validate_task(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    name = data.get("name", "").strip()
    priority = data.get("priority", "").strip()
    due_date = data.get("due_date", "")
    
    # Required name
    if not name:
        errors.append("Task name is required")
    elif len(name) > 255:
        errors.append("Task name must be under 255 characters")
    
    # Priority enum validation
    if priority:
        valid_priorities = [p.value for p in Priority]
        if priority not in valid_priorities:
            errors.append("Invalid priority")
    
    # TODO: Add datetime parsing for due_date
    
    return errors

def validate_tag(data: dict) -> list[str]:
    errors = []
    
    name = data.get("name", "").strip()
    scope = data.get("scope", "").strip()
    
    if not name:
        errors.append("Tag name is required")
    elif len(name) > 50:
        errors.append("Tag name must be under 50 characters")
    
    if scope and len(scope) > 20:
        errors.append("Tag scope must be under 20 characters")
    
    return errors