# Habit field constraints
HABIT_NAME_MAX_LENGTH = 100

HABIT_NAME_REQUIRED = "Habit name is required"
HABIT_NAME_TOO_LONG = f"Habit name must be {HABIT_NAME_MAX_LENGTH} characters or less"

STATUS_REQUIRED = "Status is required"
STATUS_INVALID = "Invalid status"

# Habit Completion
HABIT_REQUIRED = "Habit is required"
HABIT_ID_INVALID = "Invalid habit ID"

# Promotion Threshold
PROMOTION_THRESHOLD_DEFAULT = 0.7
PROMOTION_THRESHOLD_MIN = 0.0
PROMOTION_THRESHOLD_MAX = 1.0

PROMOTION_THRESHOLD_INVALID = "Promotion threshold must be a valid number"
PROMOTION_THRESHOLD_RANGE = f"Promotion threshold must be between {PROMOTION_THRESHOLD_MIN} and {PROMOTION_THRESHOLD_MAX}"

# LeetCode Record
LC_TITLE_MAX_LENGTH = 200
LC_TITLE_TOO_LONG = f"Title must not exceed {LC_TITLE_MAX_LENGTH} characters"

LC_ID_REQUIRED = "LeetCode ID is required"
LC_ID_INVALID = "LeetCode ID must be a valid number"

LC_STATUS_REQUIRED = "Status is required"
LC_STATUS_INVALID = "Invalid status"

DIFFICULTY_REQUIRED = "Difficulty required"
DIFFICULTY_INVALID = "Invalid difficulty"

LANGUAGE_REQUIRED = "Language required"
LANGUAGE_INVALID = "Invalid language"
