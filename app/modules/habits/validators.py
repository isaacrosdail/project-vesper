
from typing import Any

from app.modules.habits.constants import *
from app.modules.habits.models import (DifficultyEnum, LanguageEnum,
                                       LCStatusEnum)
from app.shared.validators import validate_enum


def validate_habit_name(name: str) -> tuple[str | None, list[str]]:
    """Required. String, max 100 chars."""
    if not name:
        return (None, [HABIT_NAME_REQUIRED])

    if len(name) > HABIT_NAME_MAX_LENGTH:
        return (None, [HABIT_NAME_TOO_LONG])

    return (name, [])


HABIT_VALIDATION_FUNCS = {
    "name": validate_habit_name,
}

def validate_habit(data: dict) -> tuple[dict, dict[str, list[str]]]:
    """Validate habit data. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in HABIT_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return (typed_data, errors)




def validate_habit_completion(data: dict) -> tuple[dict, dict[str, list[str]]]:
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




def validate_leetcode_id(leetcode_id: str) -> tuple[int | None, list[str]]:
    """Required. Valid integer ID."""
    if not leetcode_id:
        return (None, [LC_ID_REQUIRED])
    try:
        leetcode_id_int = int(leetcode_id)
    except (ValueError, TypeError):
        return (None, [LC_ID_INVALID])

    return (leetcode_id_int, [])


def validate_leetcode_title(title: str) -> tuple[str | None, list[str]]:
    """Optional. String, max 200 chars."""
    if not title:
        return (None, [])
    if len(title) > LC_TITLE_MAX_LENGTH:
        return (None, [LC_TITLE_TOO_LONG])

    return (title, [])


def validate_difficulty(difficulty: str) -> tuple[Any, list[str]]:
    """Required. Valid DifficultyEnum value."""
    return validate_enum(difficulty, DifficultyEnum, DIFFICULTY_REQUIRED, DIFFICULTY_INVALID)


def validate_language(language: str) -> tuple[Any, list[str]]:
    """Required. Valid LanguageEnum value."""
    return validate_enum(language, LanguageEnum, LANGUAGE_REQUIRED, LANGUAGE_INVALID)


def validate_leetcode_status(status: str) -> tuple[Any, list[str]]:
    """Required. Valid LCStatusEnum value."""
    return validate_enum(status, LCStatusEnum, LC_STATUS_REQUIRED, LC_STATUS_INVALID)


LC_VALIDATION_FUNCS = {
    "leetcode_id": validate_leetcode_id,
    "title": validate_leetcode_title,
    "difficulty": validate_difficulty,
    "language": validate_language,
    "status": validate_leetcode_status,
}

def validate_leetcode_record(data: dict) -> dict[str, list[str]]:
    """Validate LeetCode record. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    for field, func in LC_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return (typed_data, errors)