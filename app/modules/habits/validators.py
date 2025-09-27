
from app.modules.habits.models import StatusEnum, LCStatusEnum, DifficultyEnum, LanguageEnum
from app.modules.habits.constants import *
from app.shared.validators import validate_id_field, validate_enum


def validate_habit_name(name: str) -> list[str]:
    errors = []
    if not name:
        errors.append(HABIT_NAME_REQUIRED)
    elif len(name) > HABIT_NAME_MAX_LENGTH:
        errors.append(HABIT_NAME_TOO_LONG)
    return errors

def validate_habit_status(status: str) -> list[str]:
    if status is None: # optional
        return []
    return validate_enum(status, StatusEnum, STATUS_REQUIRED, STATUS_INVALID)

def validate_promotion_threshold(promotion_threshold: str) -> list[str]:
    errors = []
    if promotion_threshold:
        try:
            threshold = float(promotion_threshold)
            if not PROMOTION_THRESHOLD_MIN <= threshold <= PROMOTION_THRESHOLD_MAX:
                errors.append(PROMOTION_THRESHOLD_RANGE)
        except (ValueError, TypeError):
            errors.append(PROMOTION_THRESHOLD_INVALID)
    return errors

def validate_established_date(established_date: str) -> list[str]:
    errors = []
    # TODO: Add datetime validation once datetime architecture is finalized
    return errors


HABIT_VALIDATION_FUNCS = {
    "name": validate_habit_name,
    "status": validate_habit_status,
    "promotion_threshold": validate_promotion_threshold,
    "established_date": validate_established_date,
}

def validate_habit(data: dict) -> dict[str, list[str]]:
    errors = {}
    for field, func in HABIT_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    # Interdependency check
    if bool(data["status"]) != bool(data["promotion_threshold"]):
        message = "Status & promotion_threshold must either both be set or both be None"
        errors.setdefault("status", []).append(message)
        errors.setdefault("promotion_threshold", []).append(message)

    return errors


def validate_habit_completion(data: dict) -> dict[str, list[str]]:
    errors = {}
    habit_id = data.get("habit_id")
    if not habit_id:
        errors["habit_id"] = [HABIT_REQUIRED]
    else:
        try:
            int(habit_id)
        except (ValueError, TypeError):
            errors["habit_id"] = [HABIT_ID_INVALID]
    return errors


def validate_leetcode_id(leetcode_id: str) -> list[str]:
    errors = []
    if not leetcode_id:
        errors.append(LC_ID_REQUIRED)
        return errors
    try:
        int(leetcode_id)
    except (ValueError, TypeError):
        errors.append(LC_ID_INVALID)
    return errors

def validate_leetcode_title(title: str) -> list[str]:
    errors = []
    if title and len(title) > LC_TITLE_MAX_LENGTH:
        errors.append(LC_TITLE_TOO_LONG)
    return errors

def validate_difficulty(difficulty: str) -> list[str]:
    return validate_enum(difficulty, DifficultyEnum, DIFFICULTY_REQUIRED, DIFFICULTY_INVALID)

def validate_language(language: str) -> list[str]:
    return validate_enum(language, LanguageEnum, LANGUAGE_REQUIRED, LANGUAGE_INVALID)

def validate_leetcode_status(status: str) -> list[str]:
    return validate_enum(status, LCStatusEnum, LC_STATUS_REQUIRED, LC_STATUS_INVALID)

LC_VALIDATION_FUNCS = {
    "leetcode_id": validate_leetcode_id,
    "title": validate_leetcode_title,
    "difficulty": validate_difficulty,
    "language": validate_language,
    "status": validate_leetcode_status,
}

def validate_leetcode_record(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in LC_VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors

    return errors