def validate_daily_entry(data: dict) -> list[str]:
    """Validate daily entry data. Returns list of error messages."""
    errors = []
    
    # Clean data
    weight = data.get("weight", "")
    steps = data.get("steps", "")
    wake_time = data.get("wake_time", "")
    sleep_time = data.get("sleep_time", "")
    calories = data.get("calories", "")
    
    # Weight validation (optional float)
    if weight:
        try:
            weight_val = float(weight)
            if weight_val <= 0:
                errors.append("Weight must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Weight must be a valid number")
    
    # Steps validation (optional int)
    if steps:
        try:
            steps_val = int(steps)
            if steps_val < 0:
                errors.append("Steps cannot be negative")
        except (ValueError, TypeError):
            errors.append("Steps must be a valid whole number")
    
    # Calories validation (optional int)
    if calories:
        try:
            cal_val = int(calories)
            if cal_val <= 0:
                errors.append("Calories must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Calories must be a valid whole number")
    
    # TODO: Add time format validation (HH:MM format)
    
    return errors