import pytest
from app.modules.habits.validators import validate_habit, validate_habit_completion, validate_leetcode_record
from app.modules.habits.models import Status, LCStatus, Difficulty, Language

# Habit constants
HABIT_NAME_REQUIRED = "Habit name is required"
HABIT_NAME_LENGTH = "Habit name must be under 255 characters"
STATUS_INVALID = "Invalid status"
PROMOTION_THRESHOLD_INVALID = "Promotion threshold must be a valid number"
PROMOTION_THRESHOLD_RANGE = "Promotion threshold must be between 0 and 1"

# Habit completion constants
HABIT_REQUIRED = "Habit is required"
HABIT_ID_INVALID = "Invalid habit ID"

# LeetCode constants
LEETCODE_ID_REQUIRED = "LeetCode ID is required"
LEETCODE_ID_INVALID = "LeetCode ID must be a valid number"
TITLE_LENGTH = "Title must be under 255 characters"
DIFFICULTY_INVALID = "Invalid difficulty"
LANGUAGE_INVALID = "Invalid language"
LC_STATUS_INVALID = "Invalid status"

@pytest.mark.parametrize("habit_data", [
    # Basic valid habit
    {"name": "Exercise daily"},
    # With status
    {"name": "Read books", "status": "established"},
    # With promotion threshold
    {"name": "Meditate", "promotion_threshold": "0.8"},
    # Max length name
    {"name": "a" * 255},
    # All statuses
    {"name": "Habit 1", "status": "experimental"},
])
def test_validate_habit_success(habit_data):
    assert validate_habit(habit_data) == []

@pytest.mark.parametrize("habit_data,expected_errors", [
    # Missing name
    ({}, [HABIT_NAME_REQUIRED]),
    ({"status": "experimental"}, [HABIT_NAME_REQUIRED]),
    
    # Name too long
    ({"name": "a" * 256}, [HABIT_NAME_LENGTH]),
    
    # Invalid status
    ({"name": "Habit", "status": "invalid_status"}, [STATUS_INVALID]),
    
    # Invalid promotion threshold
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
    # Basic valid record
    {"leetcode_id": "1", "title": "Two Sum"},
    # With all fields
    {"leetcode_id": "2", "title": "Add Two Numbers", "difficulty": "medium", "language": "Python", "status": "solved"},
    # Minimal (just ID)
    {"leetcode_id": "100"},
])
def test_validate_leetcode_record_success(leetcode_data):
    assert validate_leetcode_record(leetcode_data) == []

@pytest.mark.parametrize("leetcode_data,expected_errors", [
    # Missing ID
    ({"title": "Problem"}, [LEETCODE_ID_REQUIRED]),
    
    # Invalid ID
    ({"leetcode_id": "not_a_number"}, [LEETCODE_ID_INVALID]),
    
    # Title too long
    ({"leetcode_id": "1", "title": "a" * 256}, [TITLE_LENGTH]),
    
    # Invalid enums
    ({"leetcode_id": "1", "difficulty": "invalid"}, [DIFFICULTY_INVALID]),
    ({"leetcode_id": "1", "language": "invalid"}, [LANGUAGE_INVALID]),
    ({"leetcode_id": "1", "status": "invalid"}, [LC_STATUS_INVALID]),
])
def test_validate_leetcode_record_errors(leetcode_data, expected_errors):
    errors = validate_leetcode_record(leetcode_data)
    assert set(errors) == set(expected_errors)