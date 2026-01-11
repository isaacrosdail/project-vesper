import pytest

from app.modules.habits import validators as v
from app.modules.habits.models import DifficultyEnum, LanguageEnum, LCStatusEnum


@pytest.mark.parametrize("habit_name, expected_value, expected_errors", [
    ("Exercise", "Exercise", []),
    ("", None, [v.HABIT_NAME_REQUIRED]),
    ("a" * 300, None, [v.HABIT_NAME_TOO_LONG])
])
def test_validate_habit_name(habit_name, expected_value, expected_errors):
    typed_value, errors = v.validate_habit_name(habit_name)
    assert typed_value == expected_value
    assert errors == expected_errors



@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"name": "Clean dishes"},
        {"name": "Clean dishes", "status": None, "promotion_threshold": None},
        {}
    ),
])
def test_validate_habit(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_habit(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors




@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    ({}, {}, {"habit_id": [v.HABIT_REQUIRED]}),
    ({"habit_id": "not_a_number"}, {}, {"habit_id": [v.HABIT_ID_INVALID]}),
])
def test_validate_habit_completion(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_habit_completion(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors




@pytest.mark.parametrize("leetcode_id, expected_value, expected_errors", [
    (None, None, [v.LC_ID_REQUIRED]),
    ("", None, [v.LC_ID_REQUIRED]),
    ("abc", None, [v.LC_ID_INVALID]),
    ("123", 123, []),
])
def test_validate_leetcode_id(leetcode_id, expected_value, expected_errors):
    typed_value, errors = v.validate_leetcode_id(leetcode_id)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("leetcode_title, expected_value, expected_errors", [
    ("", None, []),
    ("Valid Title", "Valid Title", []),
    ("a" * 256, None, [v.LC_TITLE_TOO_LONG]),
])
def test_validate_leetcode_title(leetcode_title, expected_value, expected_errors):
    typed_value, errors = v.validate_leetcode_title(leetcode_title)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("difficulty, expected_value, expected_errors", [
    (None, None, [v.DIFFICULTY_REQUIRED]),
    ("", None, [v.DIFFICULTY_REQUIRED]),
    ("EASY", DifficultyEnum.EASY, []),
    ("invalid", None, [v.DIFFICULTY_INVALID]),
])
def test_validate_difficulty(difficulty, expected_value, expected_errors):
    typed_value, errors = v.validate_difficulty(difficulty)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("language, expected_value, expected_errors", [
    (None, None, [v.LANGUAGE_REQUIRED]),
    ("", None, [v.LANGUAGE_REQUIRED]),
    ("PYTHON", LanguageEnum.PYTHON, []),
    ("JS", LanguageEnum.JS, []),
    ("other", None, [v.LANGUAGE_INVALID]),
])
def test_validate_language(language, expected_value, expected_errors):
    typed_value, errors = v.validate_language(language)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("lc_status, expected_value, expected_errors", [
    (None, None, [v.LC_STATUS_REQUIRED]),
    ("", None, [v.LC_STATUS_REQUIRED]),
    ("SOLVED", LCStatusEnum.SOLVED, []),
    ("ATTEMPTED", LCStatusEnum.ATTEMPTED, []),
    ("triedreallyhard", None, [v.LC_STATUS_INVALID]),
])
def test_validate_leetcode_status(lc_status, expected_value, expected_errors):
    typed_value, errors = v.validate_leetcode_status(lc_status)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors" , [
    # Valid
    (
        {
            "leetcode_id": "1",
            "title": "Valid",
            "difficulty": "MEDIUM",
            "language": "PYTHON",
            "status": "SOLVED"
        },
        {
            "leetcode_id": 1,
            "title": "Valid",
            "difficulty": DifficultyEnum.MEDIUM,
            "language": LanguageEnum.PYTHON,
            "status": LCStatusEnum.SOLVED
        },
        {}
    ),
    # Multiple missing
    (
        {"title": "Sample Only"},
        {"title": "Sample Only"},
        {
            "leetcode_id": [v.LC_ID_REQUIRED],
            "difficulty": [v.DIFFICULTY_REQUIRED],
            "language": [v.LANGUAGE_REQUIRED],
            "status": [v.LC_STATUS_REQUIRED]
        }
    )
])
def test_validate_leetcode_record(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_leetcode_record(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors
