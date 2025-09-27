

# Time entry constraints
CATEGORY_MAX_LENGTH = 50

CATEGORY_REQUIRED = "Category is required"
CATEGORY_TOO_LONG = f"Category must be under {CATEGORY_MAX_LENGTH} characters"

DESCRIPTION_MAX_LENGTH = 200

DESCRIPTION_LENGTH = f"Description must be under {DESCRIPTION_MAX_LENGTH} characters"

DURATION_REQUIRED = "Duration is required"
DURATION_POSITIVE = "Duration must be greater than 0"
DURATION_INVALID = "Duration must be a valid number"

# started_at / ended_at constraints
STARTED_AT_REQUIRED = "Start time is required"
STARTED_AT_INVALID = "Start time must be a valid datetime"
ENDED_AT_REQUIRED = "End time is required"
ENDED_AT_INVALID = "End time must be a valid datetime"
END_BEFORE_START = "End time must be after start time"