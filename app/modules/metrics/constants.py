
# Weight
WEIGHT_PRECISION = 5
WEIGHT_SCALE = 2
WEIGHT_MINIMUM = 0

WEIGHT_POSITIVE = "Weight must be greater than 0"
WEIGHT_INVALID = "Weight must be a valid number"

# Steps
STEPS_MINIMUM = 0
STEPS_MAX = 40_000

STEPS_NEGATIVE = "Steps cannot be negative"
STEPS_INVALID = "Steps must be a valid whole number"
STEPS_TOO_HIGH = f"Steps cannot exceed {STEPS_MAX} per day"

# Calories
CALORIES_MINIMUM = 0
CALORIES_MAX = 10_000

CALORIES_NEGATIVE = "Calories cannot be negative"
CALORIES_INVALID = "Calories must be a valid whole number"
CALORIES_TOO_HIGH = f"Calories cannot exceed {CALORIES_MAX} per day"

# Wake/Sleep datetime
# TODO: Fix, now that we have proper datetimes for these
WAKE_TIME_INVALID = "Wake time must be in HH:MM format"
SLEEP_TIME_INVALID = "Sleep time must be in HH:MM format"