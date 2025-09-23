

# Error message constants
WEIGHT_POSITIVE = "Weight must be greater than 0"
WEIGHT_INVALID = "Weight must be a valid number"
STEPS_NEGATIVE = "Steps cannot be negative"
STEPS_INVALID = "Steps must be a valid whole number"
CALORIES_POSITIVE = "Calories must be greater than 0"
CALORIES_INVALID = "Calories must be a valid whole number"
WAKE_TIME_INVALID = "Wake time must be in HH:MM format"
SLEEP_TIME_INVALID = "Sleep time must be in HH:MM format"

def validate_daily_entry(data: dict) -> list[str]:
    """Validate daily entry data. Returns list of error messages."""
    errors = []
    
    # Clean data
    weight = data.get("weight", "")
    steps = data.get("steps", "")
    wake_time = data.get("wake_time", "").strip()
    sleep_time = data.get("sleep_time", "").strip()
    calories = data.get("calories", "")
    
    # Weight (optional): Positive float
    if weight:
        try:
            weight_val = float(weight)
            if weight_val <= 0:
                errors.append(WEIGHT_POSITIVE)
        except (ValueError, TypeError):
            errors.append(WEIGHT_INVALID)
    
    # Steps validation (optional int)
    if steps:
        try:
            steps_val = int(steps)
            if steps_val < 0:
                errors.append(STEPS_NEGATIVE)
        except (ValueError, TypeError):
            errors.append(STEPS_INVALID)
    
    # Calories validation (optional int)
    if calories:
        try:
            cal_val = int(calories)
            if cal_val <= 0:
                errors.append(CALORIES_POSITIVE)
        except (ValueError, TypeError):
            errors.append(CALORIES_INVALID)
    
    # Time (optional): HH:MM format
    if wake_time:
        if not _is_valid_time_format(wake_time):
            errors.append(WAKE_TIME_INVALID)

    if sleep_time:
        if not _is_valid_time_format(sleep_time):
            errors.append(SLEEP_TIME_INVALID)
    
    return errors

def _is_valid_time_format(time_str: str) -> bool:
    try:
        from datetime import datetime
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False