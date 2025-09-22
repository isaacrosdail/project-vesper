from app.modules.habits.models import Status, LCStatus, Difficulty, Language

def validate_habit(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    name = data.get("name", "").strip()
    status = data.get("status", "").strip()
    promotion_threshold = data.get("promotion_threshold", "")
    
    # Required name
    if not name:
        errors.append("Habit name is required")
    elif len(name) > 255:
        errors.append("Habit name must be under 255 characters")
    
    # Status enum validation
    if status:
        valid_statuses = [s.value for s in Status]  # ["experimental", "established"]
        if status not in valid_statuses:
            errors.append("Invalid status")
    
    # Promotion threshold (optional float between 0 and 1)
    if promotion_threshold:
        try:
            threshold = float(promotion_threshold)
            if not 0 <= threshold <= 1:
                errors.append("Promotion threshold must be between 0 and 1")
        except (ValueError, TypeError):
            errors.append("Promotion threshold must be a valid number")
    
    return errors

def validate_habit_completion(data: dict) -> list[str]:
    errors = []
    
    habit_id = data.get("habit_id")
    
    # Habit ID validation
    if habit_id is None:
        errors.append("Habit is required")
    else:
        try:
            int(habit_id)
        except (ValueError, TypeError):
            errors.append("Invalid habit ID")
    
    return errors

def validate_leetcode_record(data: dict) -> list[str]:
    errors = []
    
    # Clean data
    leetcode_id = data.get("leetcode_id", "")
    title = data.get("title", "").strip()
    difficulty = data.get("difficulty", "").strip()
    language = data.get("language", "").strip()
    status = data.get("status", "").strip()
    
    # Required leetcode_id
    if not leetcode_id:
        errors.append("LeetCode ID is required")
    else:
        try:
            int(leetcode_id)
        except (ValueError, TypeError):
            errors.append("LeetCode ID must be a valid number")
    
    # Optional title
    if title and len(title) > 255:
        errors.append("Title must be under 255 characters")
    
    # Enum validations
    if difficulty:
        valid_difficulties = [d.value for d in Difficulty]
        if difficulty not in valid_difficulties:
            errors.append("Invalid difficulty")
    
    if language:
        valid_languages = [l.value for l in Language]
        if language not in valid_languages:
            errors.append("Invalid language")
    
    if status:
        valid_statuses = [s.value for s in LCStatus]
        if status not in valid_statuses:
            errors.append("Invalid status")
    
    return errors