import pytest
from app.modules.habits.validators import *


@pytest.mark.parametrize("habit_name, expected", [
    ("Exercise", []),
    ("", [HABIT_NAME_REQUIRED]),
    ("a" * 300, [HABIT_NAME_TOO_LONG])
])
def test_validate_habit_name(habit_name, expected):
    assert validate_habit_name(habit_name) == expected

@pytest.mark.parametrize("habit_status, expected", [
    ("ESTABLISHED", []),
    ("EXPERIMENTAL", []),
    ("", [STATUS_REQUIRED]),
    ("not_valid_status", [STATUS_INVALID])
])
def test_validate_habit_status(habit_status, expected):
    assert validate_habit_status(habit_status) == expected

@pytest.mark.parametrize("threshold, expected", [
    (None, []),
    ("0.5", []),
    ("-0.1", [PROMOTION_THRESHOLD_RANGE]),
    ("2.0", [PROMOTION_THRESHOLD_RANGE]),
    ("not_number", [PROMOTION_THRESHOLD_INVALID])
])
def test_validate_promotion_threshold(threshold, expected):
    assert validate_promotion_threshold(threshold) == expected


# TODO: test_validate_established_date?


@pytest.mark.parametrize("completion_data, expected_errors", [
    ({}, {"habit_id": [HABIT_REQUIRED]}),
    ({"habit_id": "not_a_number"}, {"habit_id": [HABIT_ID_INVALID]}),
])
def test_validate_habit_completion_errors(completion_data, expected_errors):
    assert validate_habit_completion(completion_data) == expected_errors


@pytest.mark.parametrize("leetcode_id, expected", [
    (None, [LC_ID_REQUIRED]),
    ("", [LC_ID_REQUIRED]),
    ("abc", [LC_ID_INVALID]),
    ("123", []),
])
def test_validate_leetcode_id(leetcode_id, expected):
    assert validate_leetcode_id(leetcode_id) == expected

@pytest.mark.parametrize("title, expected", [
    ("", []),
    ("Valid Title", []),
    ("a" * 256, [LC_TITLE_TOO_LONG]),
])
def test_validate_leetcode_title(title, expected):
    assert validate_leetcode_title(title) == expected


@pytest.mark.parametrize("difficulty, expected", [
    (None, [DIFFICULTY_REQUIRED]),
    ("", [DIFFICULTY_REQUIRED]),
    ("EASY", []),
    ("invalid", [DIFFICULTY_INVALID]),
])
def test_validate_difficulty(difficulty, expected):
    assert validate_difficulty(difficulty) == expected


@pytest.mark.parametrize("lang, expected", [
    (None, [LANGUAGE_REQUIRED]),
    ("", [LANGUAGE_REQUIRED]),
    ("PYTHON", []),
    ("JS", []),
    ("other", [LANGUAGE_INVALID]),
])
def test_validate_language(lang, expected):
    assert validate_language(lang) == expected


@pytest.mark.parametrize("lc_status,expected", [
    (None, [LC_STATUS_REQUIRED]),
    ("", [LC_STATUS_REQUIRED]),
    ("SOLVED", []),
    ("ATTEMPTED", []),
    ("triedreallyhard", [LC_STATUS_INVALID]),
])
def test_validate_leetcode_status(lc_status, expected):
    assert validate_leetcode_status(lc_status) == expected


def test_leetcode_record_all_valid():
    data = {
        "leetcode_id": "1",
        "title": "Valid",
        "difficulty": "MEDIUM",
        "language": "PYTHON",
        "status": "SOLVED"
    }
    assert validate_leetcode_record(data) == {}

def test_validate_leetcode_record_multiple_missing():
    data = {"title": "Sample Only"}
    errors = validate_leetcode_record(data)
    assert set(errors.keys()) == {"leetcode_id", "difficulty", "language", "status"}