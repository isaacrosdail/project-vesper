

# Task constraints
TASK_NAME_MAX_LENGTH = 150

TASK_NAME_REQUIRED = "Task name is required"
TASK_NAME_TOO_LONG = f"Task name must be under {TASK_NAME_MAX_LENGTH} characters"

PRIORITY_REQUIRED = "Priority is required"
PRIORITY_INVALID = "Invalid priority"
DUE_DATE_INVALID = "Due date must be a valid datetime"

# Tag constraints
TAG_NAME_MAX_LENGTH = 50
TAG_SCOPE_MAX_LENGTH = 20

TAG_NAME_REQUIRED = "Tag name is required"
TAG_NAME_LENGTH = f"Tag name must be under {TAG_NAME_MAX_LENGTH} characters"
TAG_SCOPE_LENGTH = f"Tag scope must be under {TAG_SCOPE_MAX_LENGTH} characters"