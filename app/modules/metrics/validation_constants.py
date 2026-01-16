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
TIME_HHMM_INVALID = "Time must be in HH:MM format"
TIME_HHMM_DIGITS = "Wake time must contain only digits"
TIME_HHMM_HOUR = "Hour must be 00-23"
TIME_HHMM_MINUTE = "Minute must be 00-59"
