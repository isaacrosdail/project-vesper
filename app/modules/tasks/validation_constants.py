# Task
TASK_NAME_MAX_LENGTH = 150

TASK_NAME_REQUIRED = "Task name is required"
TASK_NAME_TOO_LONG = f"Task name must not exceed {TASK_NAME_MAX_LENGTH} characters"

PRIORITY_REQUIRED = "Priority is required"
PRIORITY_REQUIRED_NON_FROG = "Priority is required for non-frog tasks"
PRIORITY_INVALID = "Invalid priority"

FROG_REQUIRES_DUE_DATE = "Frog tasks must have a due date"
FROG_REQUIRES_NO_PRIORITY = "Frog tasks cannot have a priority"
DUE_DATE_INVALID = "Due date must be a valid datetime"


# Tag
TAG_NAME_MAX_LENGTH = 50
TAG_SCOPE_MAX_LENGTH = 20

TAG_NAME_REQUIRED = "Tag name is required"
TAG_NAME_LENGTH = f"Tag name must not exceed {TAG_NAME_MAX_LENGTH} characters"
TAG_SCOPE_LENGTH = f"Tag scope must not exceed {TAG_SCOPE_MAX_LENGTH} characters"
