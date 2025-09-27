
# Habit field constraints
HABIT_NAME_MAX_LENGTH = 100
PROMOTION_THRESHOLD_DEFAULT = 0.7
PROMOTION_THRESHOLD_MIN = 0.0
PROMOTION_THRESHOLD_MAX = 1.0

# LeetCode Record Field constraints
LC_TITLE_MAX_LENGTH = 200

# Habit constants
HABIT_NAME_REQUIRED = "Habit name is required"
HABIT_NAME_TOO_LONG = f"Habit name must be {HABIT_NAME_MAX_LENGTH} characters or less"
STATUS_REQUIRED = "Status is required"
STATUS_INVALID = "Invalid status"

PROMOTION_THRESHOLD_INVALID = "Promotion threshold must be a valid number"
PROMOTION_THRESHOLD_RANGE = f"Promotion threshold must be between {PROMOTION_THRESHOLD_MIN} and {PROMOTION_THRESHOLD_MAX}"

# Habit completion constants
HABIT_REQUIRED = "Habit is required"
HABIT_ID_INVALID = "Invalid habit ID"

# LeetCode (LC_*) constants
LC_ID_REQUIRED = "LeetCode ID is required"
LC_ID_INVALID = "LeetCode ID must be a valid number"
LC_TITLE_TOO_LONG = f"Title must be under {LC_TITLE_MAX_LENGTH} characters"
LC_STATUS_INVALID = "Invalid status"
LC_STATUS_REQUIRED = "Status is required"

DIFFICULTY_INVALID = "Invalid difficulty"
DIFFICULTY_REQUIRED = "Difficulty required"
LANGUAGE_INVALID = "Invalid language"
LANGUAGE_REQUIRED = "Language required"
