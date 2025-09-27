import pytest
from app.modules.time_tracking.validators import *


@pytest.mark.parametrize("category, expected", [
    ("Programming", []),
    ("", [CATEGORY_REQUIRED]),
    ("a" * 51, [CATEGORY_TOO_LONG]),
])
def test_validate_category(category, expected):
    assert validate_category(category) == expected


@pytest.mark.parametrize("description, expected", [
    (None, []),
    ("", []),
    ("Some description", []),
    ("a" * 201, [DESCRIPTION_LENGTH]),
])
def test_validate_description(description, expected):
    assert validate_description(description) == expected


@pytest.mark.parametrize("duration_minutes, expected", [
    ("60", []),
    ("0.5", []),
    ("-5", [DURATION_POSITIVE]),
    ("0", [DURATION_POSITIVE]),
    ("not_a_number", [DURATION_INVALID]),
    ("", [DURATION_REQUIRED]),
    (None, [DURATION_REQUIRED]),
])
def test_validate_duration_minutes(duration_minutes, expected):
    assert validate_duration_minutes(duration_minutes) == expected


@pytest.mark.parametrize("data, expected", [
    ({"category": "Study", "description": "Algorithms", "duration_minutes": "45"}, {})
])
def test_validate_time_entry_valid(data, expected):
    assert validate_time_entry(data) == expected


@pytest.mark.parametrize("data, expected", [
    ({"category": "", "description": "a" * 201, "duration_minutes": "-5"}, 
    {
        "category": [CATEGORY_REQUIRED],
        "description": [DESCRIPTION_LENGTH],
        "duration_minutes": [DURATION_POSITIVE]
    })
])
def test_validate_time_entry_combined_errors(data, expected):
    assert validate_time_entry(data) == expected
