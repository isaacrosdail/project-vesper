from typing import Any

from app.modules.habits import validation_constants as c
from app.modules.habits.models import (
    DifficultyEnum,
    LanguageEnum,
    LCStatusEnum,
    StatusEnum,
)
from app.shared.decorators import log_validator
from app.shared.validators import validate_enum

# TODO: Find a proper home
TARGET_FREQ_MIN = 1
TARGET_FREQ_MAX = 7


def validate_habit_name(name: str | None) -> tuple[str | None, list[str]]:
    """Required. String, max 100 chars."""
    if not name:
        return (None, [c.HABIT_NAME_REQUIRED])

    if len(name) > c.HABIT_NAME_MAX_LENGTH:
        return (None, [c.HABIT_NAME_TOO_LONG])

    return (name, [])


def validate_target_frequency(
    target_frequency: int | str | None,
) -> tuple[int | None, list[str]]:
    """Required."""
    if target_frequency is None or target_frequency == "":
        return (None, ["target_frequency required"])

    try:
        freq = int(target_frequency)
    except (ValueError, TypeError):
        return (None, ["target_frequency must be an integer"])

    if not (TARGET_FREQ_MIN <= freq <= TARGET_FREQ_MAX):
        return (
            None,
            [
                f"target_frequency must be between {TARGET_FREQ_MIN} and {TARGET_FREQ_MAX}"
            ],
        )

    return (freq, [])


HABIT_VALIDATION_FUNCS = {
    "name": validate_habit_name,
    "target_frequency": validate_target_frequency,
}


@log_validator
def validate_habit(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate and transform habit data. Returns (typed_data, errors).

    Applies (or removes) `status` and `promotion_threshold` based on presence (or absence) of
    transient `is_promotable` flag.

    Returns:
        Tuple of (typed_data, errors)
    """
    typed_data: dict[str, Any] = {}
    errors = {}

    for field, func in HABIT_VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        else:
            typed_data[field] = typed_value

    if data.get("is_promotable"):
        typed_data["status"] = StatusEnum.EXPERIMENTAL
        typed_data["promotion_threshold"] = c.PROMOTION_THRESHOLD_DEFAULT
    else:
        typed_data["status"] = None
        typed_data["promotion_threshold"] = None

    return (typed_data, errors)


@log_validator
def validate_habit_completion(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Validate habit completion. Returns (typed_data, errors)."""
    typed_data = {}
    errors = {}

    habit_id = data.get("habit_id")
    if not habit_id:
        errors["habit_id"] = [c.HABIT_REQUIRED]
    else:
        try:
            habit_id_int = int(habit_id)
            typed_data["habit_id"] = habit_id_int
        except (ValueError, TypeError):
            errors["habit_id"] = [c.HABIT_ID_INVALID]

    return (typed_data, errors)


def validate_leetcode_id(leetcode_id: str | None) -> tuple[int | None, list[str]]:
    """Required. Valid integer ID."""
    if not leetcode_id:
        return (None, [c.LC_ID_REQUIRED])
    try:
        leetcode_id_int = int(leetcode_id)
    except (ValueError, TypeError):
        return (None, [c.LC_ID_INVALID])

    return (leetcode_id_int, [])


def validate_leetcode_title(title: str | None) -> tuple[str | None, list[str]]:
    """Optional. String, max 200 chars."""
    if not title:
        return (None, [])
    if len(title) > c.LC_TITLE_MAX_LENGTH:
        return (None, [c.LC_TITLE_TOO_LONG])

    return (title, [])


def validate_difficulty(difficulty: str | None) -> tuple[Any, list[str]]:
    """Required. Valid DifficultyEnum value."""
    if not difficulty:
        return (None, [c.DIFFICULTY_REQUIRED])
    return validate_enum(difficulty, DifficultyEnum, c.DIFFICULTY_INVALID)


def validate_language(language: str | None) -> tuple[Any, list[str]]:
    """Required. Valid LanguageEnum value."""
    if not language:
        return (None, [c.LANGUAGE_REQUIRED])
    return validate_enum(language, LanguageEnum, c.LANGUAGE_INVALID)


def validate_leetcode_status(status: str | None) -> tuple[Any, list[str]]:
    """Required. Valid LCStatusEnum value."""
    if not status:
        return (None, [c.LC_STATUS_REQUIRED])
    return validate_enum(status, LCStatusEnum, c.LC_STATUS_INVALID)


LC_VALIDATION_FUNCS = {
    "leetcode_id": validate_leetcode_id,
    "title": validate_leetcode_title,
    "difficulty": validate_difficulty,
    "language": validate_language,
    "status": validate_leetcode_status,
}


@log_validator
def validate_leetcode_record(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
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
