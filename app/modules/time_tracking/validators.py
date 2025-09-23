
from datetime import datetime

# Time entry validation constants
CATEGORY_REQUIRED = "Category is required"
CATEGORY_LENGTH = "Category must be under 50 characters"
DESCRIPTION_LENGTH = "Description must be under 200 characters"
DURATION_REQUIRED = "Duration is required"
DURATION_POSITIVE = "Duration must be greater than 0"
DURATION_INVALID = "Duration must be a valid number"
STARTED_AT_REQUIRED = "Start time is required"
STARTED_AT_INVALID = "Start time must be a valid datetime"
ENDED_AT_REQUIRED = "End time is required"
ENDED_AT_INVALID = "End time must be a valid datetime"
END_BEFORE_START = "End time must be after start time"


def validate_time_entry(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    category = data.get("category", "").strip()
    description = data.get("description", "").strip()
    duration = data.get("duration", "")
    started_at = data.get("started_at", "").strip()
    ended_at = data.get("ended_at", "").strip()
    
    # Category: Required, max 50 chars
    if not category:
        errors.append(CATEGORY_REQUIRED)
    if category and len(category) > 50:
        errors.append(CATEGORY_LENGTH)
    
    # Description (optional): max 200 chars
    if description and len(description) > 200:
        errors.append(DESCRIPTION_LENGTH)
    
    # Duration: Required, positive float
    if not duration:
        errors.append(DURATION_REQUIRED)
    if duration:
        try:
            duration_val = float(duration)
            if duration_val <= 0:
                errors.append(DURATION_POSITIVE)
        except (ValueError, TypeError):
            errors.append(DURATION_INVALID)
    
    # TODO: Add datetime validation for started_at/ended_at
    
    return errors