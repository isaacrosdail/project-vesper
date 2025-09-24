import pytest
from app.modules.habits.validators import *


@pytest.mark.parametrize("habit_data", [
    {"name": "Exercise daily"},
    {"name": "Read books", "status": "established"},
    {"name": "Meditate", "promotion_threshold": "0.8"},
    {"name": "a" * 255},
    {"name": "Habit 1", "status": "experimental"},
])
def test_validate_habit_success(habit_data):
    assert validate_habit(habit_data) == []

@pytest.mark.parametrize("habit_data,expected_errors", [
    ({}, [HABIT_NAME_REQUIRED]),
    ({"status": "experimental"}, [HABIT_NAME_REQUIRED]),
    ({"name": "a" * 256}, [HABIT_NAME_LENGTH]),
    ({"name": "Habit", "status": "invalid_status"}, [STATUS_INVALID]),
    ({"name": "Habit", "promotion_threshold": "not_a_number"}, [PROMOTION_THRESHOLD_INVALID]),
    ({"name": "Habit", "promotion_threshold": "-0.1"}, [PROMOTION_THRESHOLD_RANGE]),
    ({"name": "Habit", "promotion_threshold": "1.1"}, [PROMOTION_THRESHOLD_RANGE]),
])
def test_validate_habit_errors(habit_data, expected_errors):
    errors = validate_habit(habit_data)
    assert set(errors) == set(expected_errors)

@pytest.mark.parametrize("completion_data", [
    # Basic valid completion
    {"habit_id": "123"},
])
def test_validate_habit_completion_success(completion_data):
    assert validate_habit_completion(completion_data) == []

@pytest.mark.parametrize("completion_data,expected_errors", [
    # Missing habit_id
    ({}, [HABIT_REQUIRED]),
    
    # Invalid habit_id
    ({"habit_id": "not_a_number"}, [HABIT_ID_INVALID]),
])
def test_validate_habit_completion_errors(completion_data, expected_errors):
    errors = validate_habit_completion(completion_data)
    for expected_error in expected_errors:
        assert expected_error in errors

@pytest.mark.parametrize("leetcode_data", [
    # All fields valid
    {
        "leetcode_id": "2",
        "title": "Add Two Numbers",
        "difficulty": "medium",
        "language": "Python",
        "status": "solved",
    },
    # Title optional, but enums present
    {
        "leetcode_id": "3",
        "difficulty": "easy",
        "language": "JavaScript",
        "status": "attempted",
    },
])
def test_validate_leetcode_record_success(leetcode_data):
    assert validate_leetcode_record(leetcode_data) == []

@pytest.mark.parametrize("leetcode_data,expected_errors", [
    ({"title": "Problem"},
     [LEETCODE_ID_REQUIRED, DIFFICULTY_REQUIRED, LANGUAGE_REQUIRED, LC_STATUS_REQUIRED]),
    ({"leetcode_id": "not_a_number", "difficulty": "easy", "language": "Python", "status": "solved"},
     [LEETCODE_ID_INVALID]),
    ({"leetcode_id": "1", "title": "a" * 256, "difficulty": "easy", "language": "Python", "status": "solved"},
     [TITLE_LENGTH]),
    ({"leetcode_id": "1"}, [DIFFICULTY_REQUIRED, LANGUAGE_REQUIRED, LC_STATUS_REQUIRED]),
    ({"leetcode_id": "1", "difficulty": "invalid", "language": "Python", "status": "solved"},
     [DIFFICULTY_INVALID]),
    ({"leetcode_id": "1", "difficulty": "easy", "language": "invalid", "status": "solved"},
     [LANGUAGE_INVALID]),
    ({"leetcode_id": "1", "difficulty": "easy", "language": "Python", "status": "invalid"},
     [LC_STATUS_INVALID]),
])
def test_validate_leetcode_record_errors(leetcode_data, expected_errors):
    errors = validate_leetcode_record(leetcode_data)
    assert set(errors) == set(expected_errors)