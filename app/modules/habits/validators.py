
from app.modules.habits.models import Status, LCStatus, Difficulty, Language

# Habit constants
HABIT_NAME_REQUIRED = "Habit name is required"
HABIT_NAME_LENGTH = "Habit name must be under 255 characters"
STATUS_INVALID = "Invalid status"
PROMOTION_THRESHOLD_INVALID = "Promotion threshold must be a valid number"
PROMOTION_THRESHOLD_RANGE = "Promotion threshold must be between 0 and 1"

# Habit completion constants
HABIT_REQUIRED = "Habit is required"
HABIT_ID_INVALID = "Invalid habit ID"

# LeetCode constants
LEETCODE_ID_REQUIRED = "LeetCode ID is required"
LEETCODE_ID_INVALID = "LeetCode ID must be a valid number"
TITLE_LENGTH = "Title must be under 255 characters"

DIFFICULTY_INVALID = "Invalid difficulty"
DIFFICULTY_REQUIRED = "Difficulty required"
LANGUAGE_INVALID = "Invalid language"
LANGUAGE_REQUIRED = "Language required"
LC_STATUS_INVALID = "Invalid status"
LC_STATUS_REQUIRED = "Language required"

def validate_habit(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    name = data.get("name", "").strip()
    status = data.get("status", "").strip()
    promotion_threshold = data.get("promotion_threshold", "")
    
    # Name: Required, max 255 chars
    if not name:
        errors.append(HABIT_NAME_REQUIRED)
    if name and len(name) > 255:
        errors.append(HABIT_NAME_LENGTH)
    
    # Status (optional): Valid enum
    if status:
        valid_statuses = [s.value for s in Status]
        if status not in valid_statuses:
            errors.append(STATUS_INVALID)
    
    # Promotion threshold (optional): Float, between 0-1 (incl.)
    if promotion_threshold:
        try:
            threshold = float(promotion_threshold)
            if not 0 <= threshold <= 1:
                errors.append(PROMOTION_THRESHOLD_RANGE)
        except (ValueError, TypeError):
            errors.append(PROMOTION_THRESHOLD_INVALID)
    
    return errors

def validate_habit_completion(data: dict) -> list[str]:
    errors = []
    
    habit_id = data.get("habit_id")
    
    # Habit ID: Required
    # TODO: Will need to simply enforce this in service layer
    if habit_id is None:
        errors.append(HABIT_REQUIRED)
    if habit_id is not None:
        try:
            int(habit_id)
        except (ValueError, TypeError):
            errors.append(HABIT_ID_INVALID)
    
    return errors

def validate_leetcode_record(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    leetcode_id = data.get("leetcode_id", "")
    title = data.get("title", "").strip()
    difficulty = data.get("difficulty", "").strip()
    language = data.get("language", "").strip()
    status = data.get("status", "").strip()
    
    # Leetcode_id: Required
    if not leetcode_id:
        errors.append(LEETCODE_ID_REQUIRED)
    if leetcode_id:
        try:
            int(leetcode_id)
        except (ValueError, TypeError):
            errors.append(LEETCODE_ID_INVALID)
    
    # Title (optional): max 255 chars
    if title and len(title) > 255:
        errors.append(TITLE_LENGTH)
    
    # Enums: All required, all valid enums
    if not difficulty:
        errors.append(DIFFICULTY_REQUIRED)
    if difficulty:
        valid_difficulties = [d.value for d in Difficulty]
        if difficulty not in valid_difficulties:
            errors.append(DIFFICULTY_INVALID)

    if not language:
        errors.append(LANGUAGE_REQUIRED)
    if language:
        valid_languages = [l.value for l in Language]
        if language not in valid_languages:
            errors.append(LANGUAGE_INVALID)

    if not status:
        errors.append(LC_STATUS_REQUIRED)
    if status:
        valid_statuses = [s.value for s in LCStatus]
        if status not in valid_statuses:
            errors.append(LC_STATUS_INVALID)
    
    return errors