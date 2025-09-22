
def validate_time_entry(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    category = data.get("category", "").strip()
    description = data.get("description", "").strip()
    duration = data.get("duration", "")
    
    # Required category
    if not category:
        errors.append("Category is required")
    elif len(category) > 50:
        errors.append("Category must be under 50 characters")
    
    # Optional description
    if description and len(description) > 200:
        errors.append("Description must be under 200 characters")
    
    # Duration validation (required float)
    if not duration:
        errors.append("Duration is required")
    else:
        try:
            duration_val = float(duration)
            if duration_val <= 0:
                errors.append("Duration must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Duration must be a valid number")
    
    # TODO: Add datetime validation for started_at/ended_at
    
    return errors