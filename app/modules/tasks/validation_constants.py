
from app.shared.validation_messages import invalid, required, too_long

# Task
TASK_NAME_MAX_LENGTH = 150

TASK_NAME_REQUIRED = required("Task name")
TASK_NAME_TOO_LONG = too_long("Task name", TASK_NAME_MAX_LENGTH)

PRIORITY_REQUIRED = required("Priority")
PRIORITY_REQUIRED_NON_FROG = "Priority is required for non-frog tasks"
PRIORITY_INVALID = invalid("Priority")

FROG_REQUIRES_DUE_DATE = "Frog tasks must have a due date"
FROG_REQUIRES_NO_PRIORITY = "Frog tasks cannot have a priority"
DUE_DATE_INVALID = "Due date must be a valid datetime"

# Tag
TAG_NAME_MAX_LENGTH = 50
TAG_SCOPE_MAX_LENGTH = 20

TAG_NAME_REQUIRED = required("Tag name")
TAG_NAME_LENGTH = too_long("Tag name", TAG_NAME_MAX_LENGTH)
TAG_SCOPE_LENGTH = too_long("Tag scope", TAG_SCOPE_MAX_LENGTH)
