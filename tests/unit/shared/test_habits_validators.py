import pytest

from app.modules.habits.validators import *


@pytest.mark.parametrize("habit_name, expected_value, expected_errors", [
    ("Exercise", "Exercise", []),
    ("", None, [HABIT_NAME_REQUIRED]),
    ("a" * 300, None, [HABIT_NAME_TOO_LONG])
])
def test_validate_habit_name(habit_name, expected_value, expected_errors):
    typed_value, errors = validate_habit_name(habit_name)
    assert typed_value == expected_value
    assert errors == expected_errors



@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"name": "Clean dishes"},
        {"name": "Clean dishes"},
        {}
    ),
    (
        {"name": "Clean dishes"},
        {"name": "Clean dishes"},
        {}
    ),
])
def test_validate_habit(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_habit(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors




@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    ({}, {}, {"habit_id": [HABIT_REQUIRED]}),
    ({"habit_id": "not_a_number"}, {}, {"habit_id": [HABIT_ID_INVALID]}),
])
def test_validate_habit_completion(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_habit_completion(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors




@pytest.mark.parametrize("leetcode_id, expected_value, expected_errors", [
    (None, None, [LC_ID_REQUIRED]),
    ("", None, [LC_ID_REQUIRED]),
    ("abc", None, [LC_ID_INVALID]),
    ("123", 123, []),
])
def test_validate_leetcode_id(leetcode_id, expected_value, expected_errors):
    typed_value, errors = validate_leetcode_id(leetcode_id)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("leetcode_title, expected_value, expected_errors", [
    ("", None, []),
    ("Valid Title", "Valid Title", []),
    ("a" * 256, None, [LC_TITLE_TOO_LONG]),
])
def test_validate_leetcode_title(leetcode_title, expected_value, expected_errors):
    typed_value, errors = validate_leetcode_title(leetcode_title)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("difficulty, expected_value, expected_errors", [
    (None, None, [DIFFICULTY_REQUIRED]),
    ("", None, [DIFFICULTY_REQUIRED]),
    ("EASY", DifficultyEnum.EASY, []),
    ("invalid", None, [DIFFICULTY_INVALID]),
])
def test_validate_difficulty(difficulty, expected_value, expected_errors):
    typed_value, errors = validate_difficulty(difficulty)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("language, expected_value, expected_errors", [
    (None, None, [LANGUAGE_REQUIRED]),
    ("", None, [LANGUAGE_REQUIRED]),
    ("PYTHON", LanguageEnum.PYTHON, []),
    ("JS", LanguageEnum.JS, []),
    ("other", None, [LANGUAGE_INVALID]),
])
def test_validate_language(language, expected_value, expected_errors):
    typed_value, errors = validate_language(language)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("lc_status, expected_value, expected_errors", [
    (None, None, [LC_STATUS_REQUIRED]),
    ("", None, [LC_STATUS_REQUIRED]),
    ("SOLVED", LCStatusEnum.SOLVED, []),
    ("ATTEMPTED", LCStatusEnum.ATTEMPTED, []),
    ("triedreallyhard", None, [LC_STATUS_INVALID]),
])
def test_validate_leetcode_status(lc_status, expected_value, expected_errors):
    typed_value, errors = validate_leetcode_status(lc_status)
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
            "leetcode_id": [LC_ID_REQUIRED],
            "difficulty": [DIFFICULTY_REQUIRED],
            "language": [LANGUAGE_REQUIRED],
            "status": [LC_STATUS_REQUIRED]
        }
    )
])
def test_validate_leetcode_record(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_leetcode_record(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors