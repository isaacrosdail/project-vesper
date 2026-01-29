

from app.shared.validation_messages import positive, required, too_long

# Time entry constraints
CATEGORY_MAX_LENGTH = 50
CATEGORY_REQUIRED = required("Category")
CATEGORY_TOO_LONG = too_long("Category", CATEGORY_MAX_LENGTH)

# Description
DESCRIPTION_MAX_LENGTH = 200
DESCRIPTION_LENGTH = too_long("Description", DESCRIPTION_MAX_LENGTH)

# Duration minutes
DURATION_REQUIRED = required("Duration")
DURATION_POSITIVE = positive("Duration")
DURATION_INVALID = "Duration must be a valid number"

# Started / Ended
STARTED_AT_REQUIRED = required("Start time")
STARTED_AT_INVALID = "Start time must be a valid datetime"

ENDED_AT_REQUIRED = required("End time")
ENDED_AT_INVALID = "End time must be a valid datetime"
END_BEFORE_START = "End time must be after start time"
