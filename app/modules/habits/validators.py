
from typing import Any

from app.modules.habits.constants import *
from app.modules.habits.models import (DifficultyEnum, LanguageEnum,
                                       LCStatusEnum, StatusEnum)
from app.shared.decorators import log_validator
from app.shared.validators import validate_enum


def validate_habit_name(name: str | None) -> tuple[str | None, list[str]]:
    """Required. String, max 100 chars."""
    if not name:
        return (None, [HABIT_NAME_REQUIRED])

    if len(name) > HABIT_NAME_MAX_LENGTH:
        return (None, [HABIT_NAME_TOO_LONG])

    return (name, [])

def validate_target_frequency(target_frequency: int | str | None) -> tuple[int | None, list[str]]:
    """Required."""
    if target_frequency is None or target_frequency == "":
        return (None, ["target_frequency required"])
    
    try:
        freq = int(target_frequency)
    except (ValueError, TypeError):
        return (None, ["target_frequency must be an integer"])

    if not (1 <= freq <= 7):
        return (None, ["target_frequency must be between 1 and 7"])
    
    return (freq, [])

HABIT_VALIDATION_FUNCS = {
    "name": validate_habit_name,
    "target_frequency": validate_target_frequency,
}
@log_validator
def validate_habit(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate habit data. Returns (typed_data, errors)."""
    typed_data: dict[str, Any] = {}
    errors = {}

    for field, func in HABIT_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    # Apply app-defined values if habit is marked promotable (transient flag, not persisted)
    if data.get("is_promotable"):
        typed_data["status"] = StatusEnum.EXPERIMENTAL
        typed_data["promotion_threshold"] = PROMOTION_THRESHOLD_DEFAULT
    # And clear them upon updates where is_promotable is unchecked
    else:
        typed_data["status"] = None
        typed_data["promotion_threshold"] = None

    return (typed_data, errors)



@log_validator
def validate_habit_completion(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate habit completion. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}
    
    habit_id = data.get("habit_id")
    if not habit_id:
        errors["habit_id"] = [HABIT_REQUIRED]
    else:
        try:
            habit_id_int = int(habit_id)
            typed_data["habit_id"] = habit_id_int
        except (ValueError, TypeError):
            errors["habit_id"] = [HABIT_ID_INVALID]

    return (typed_data, errors)




def validate_leetcode_id(leetcode_id: str | None) -> tuple[int | None, list[str]]:
    """Required. Valid integer ID."""
    if not leetcode_id:
        return (None, [LC_ID_REQUIRED])
    try:
        leetcode_id_int = int(leetcode_id)
    except (ValueError, TypeError):
        return (None, [LC_ID_INVALID])

    return (leetcode_id_int, [])


def validate_leetcode_title(title: str | None) -> tuple[str | None, list[str]]:
    """Optional. String, max 200 chars."""
    if not title:
        return (None, [])
    if len(title) > LC_TITLE_MAX_LENGTH:
        return (None, [LC_TITLE_TOO_LONG])

    return (title, [])


def validate_difficulty(difficulty: str | None) -> tuple[Any, list[str]]:
    if not difficulty:
        return (None, [DIFFICULTY_REQUIRED])
    """Required. Valid DifficultyEnum value."""
    return validate_enum(difficulty, DifficultyEnum, DIFFICULTY_REQUIRED, DIFFICULTY_INVALID)


def validate_language(language: str | None) -> tuple[Any, list[str]]:
    if not language:
        return (None, [LANGUAGE_REQUIRED])
    """Required. Valid LanguageEnum value."""
    return validate_enum(language, LanguageEnum, LANGUAGE_REQUIRED, LANGUAGE_INVALID)


def validate_leetcode_status(status: str | None) -> tuple[Any, list[str]]:
    if not status:
        return (None, [LC_STATUS_REQUIRED])
    """Required. Valid LCStatusEnum value."""
    return validate_enum(status, LCStatusEnum, LC_STATUS_REQUIRED, LC_STATUS_INVALID)


LC_VALIDATION_FUNCS = {
    "leetcode_id": validate_leetcode_id,
    "title": validate_leetcode_title,
    "difficulty": validate_difficulty,
    "language": validate_language,
    "status": validate_leetcode_status,
}
@log_validator
def validate_leetcode_record(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate LeetCode record. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in LC_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    return (typed_data, errors)