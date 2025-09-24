import pytest
from app.modules.time_tracking.validators import *


@pytest.mark.parametrize("entry_data", [
    # Basic valid entry
    {"category": "Programming", "duration": "60"},
    # With description
    {"category": "Workout", "description": "Morning run", "duration": "30"},
    # Edge cases
    {"category": "a" * 50, "duration": "0.5"},  # Max category length, decimal duration
    {"category": "Reading", "description": "a" * 200, "duration": "120"},  # Max description length
])
def test_validate_time_entry_success(entry_data):
    assert validate_time_entry(entry_data) == []

@pytest.mark.parametrize("entry_data,expected_errors", [
    # Missing required fields
    ({"duration": "60"}, [CATEGORY_REQUIRED]),
    ({"category": "Programming"}, [DURATION_REQUIRED]),
    
    # Category validation
    ({"category": "", "duration": "60"}, [CATEGORY_REQUIRED]),
    ({"category": "a" * 51, "duration": "60"}, [CATEGORY_LENGTH]),
    
    # Description validation
    ({"category": "Work", "description": "a" * 201, "duration": "60"}, [DESCRIPTION_LENGTH]),
    
    # Duration validation
    ({"category": "Programming", "duration": "0"}, [DURATION_POSITIVE]),
    ({"category": "Programming", "duration": "-30"}, [DURATION_POSITIVE]),
    ({"category": "Programming", "duration": "not_a_number"}, [DURATION_INVALID]),
])
def test_validate_time_entry_errors(entry_data, expected_errors):
    errors = validate_time_entry(entry_data)
    assert set(errors) == set(expected_errors)