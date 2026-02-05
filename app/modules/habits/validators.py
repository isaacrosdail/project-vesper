from typing import Any

from app.modules.habits import validation_constants as c
from app.modules.habits.models import (
    DifficultyEnum,
    LanguageEnum,
    LCStatusEnum,
    StatusEnum,
)
from app.shared.decorators import log_validator
from app.shared.validators import (
    validate_required_int, validate_optional_string, validate_required_string,
    validate_required_enum
)
from app.shared.type_defs import ValidatorFunc


HABIT_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "name": lambda v: validate_required_string(
        v, c.HABIT_NAME_MAX_LENGTH, c.HABIT_NAME_REQUIRED, c.HABIT_NAME_TOO_LONG
    ),
    "target_frequency": lambda v: validate_required_int(
        v, c.TARGET_FREQ_INVALID, c.TARGET_FREQ_REQUIRED
    ),
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
        typed_data["promotion_threshold"] = 0.7
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


LC_VALIDATION_FUNCS: dict[str, ValidatorFunc] = {
    "leetcode_id": lambda v: validate_required_int(
        v, c.LC_ID_INVALID, c.LC_ID_REQUIRED
    ),
    "title": lambda v: validate_optional_string(
        v, c.LC_TITLE_MAX_LENGTH, c.LC_TITLE_TOO_LONG
    ),
    "difficulty": lambda v: validate_required_enum(
        v, DifficultyEnum, c.DIFFICULTY_INVALID, c.DIFFICULTY_REQUIRED
    ),
    "language": lambda v: validate_required_enum(
        v, LanguageEnum, c.LANGUAGE_INVALID, c.LANGUAGE_REQUIRED
    ),
    "status": lambda v: validate_required_enum(
        v, LCStatusEnum, c.LC_STATUS_INVALID, c.LC_STATUS_REQUIRED
    ),
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
