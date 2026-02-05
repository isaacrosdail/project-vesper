
from app.shared.validation_messages import invalid, required, too_long

# Habit field constraints
HABIT_NAME_MAX_LENGTH = 100

HABIT_NAME_REQUIRED = required("Habit name")
HABIT_NAME_TOO_LONG = too_long("Habit name", HABIT_NAME_MAX_LENGTH)

STATUS_REQUIRED = required("Status")
STATUS_INVALID = invalid("Status")

TARGET_FREQ_REQUIRED = required("Target frequency")
TARGET_FREQ_INVALID = invalid("Target frequency")

# Habit Completion
HABIT_REQUIRED = required("Habit")
HABIT_ID_INVALID = invalid("Habit ID")

# LeetCode Record
LC_TITLE_MAX_LENGTH = 200
LC_TITLE_TOO_LONG = too_long("Title", LC_TITLE_MAX_LENGTH)

LC_ID_REQUIRED = required("LeetCode ID")
LC_ID_INVALID = invalid("LeetCode ID")

LC_STATUS_REQUIRED = required("Status")
LC_STATUS_INVALID = invalid("Status")

DIFFICULTY_REQUIRED = required("Difficulty")
DIFFICULTY_INVALID = invalid("Difficulty")

LANGUAGE_REQUIRED = required("Language")
LANGUAGE_INVALID = invalid("Language")
