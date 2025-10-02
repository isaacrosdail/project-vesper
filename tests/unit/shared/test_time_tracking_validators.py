import pytest
from app.modules.time_tracking.validators import *


@pytest.mark.parametrize("category, expected_value, expected_errors", [
    ("Programming", "Programming", []),
    ("", None, [CATEGORY_REQUIRED]),
    ("a" * 51, None, [CATEGORY_TOO_LONG]),
])
def test_validate_category(category, expected_value, expected_errors):
    typed_value, errors = validate_category(category)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("description, expected_value, expected_errors", [
    (None, None, []),
    ("", None, []),
    ("Some description", "Some description", []),
    ("a" * 201, None, [DESCRIPTION_LENGTH]),
])
def test_validate_description(description, expected_value, expected_errors):
    typed_value, errors = validate_description(description)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.skip(reason="Implement validators for this")
def test_validate_start_end():
    pass


@pytest.mark.parametrize("duration_minutes, expected_value, expected_errors", [
    ("60", 60, []),
    ("0.5", None, [DURATION_INVALID]),
    ("-5", None, [DURATION_POSITIVE]),
    ("0", None, [DURATION_POSITIVE]),
    ("not_a_number", None, [DURATION_INVALID]),
    ("", None, [DURATION_REQUIRED]),
    (None, None, [DURATION_REQUIRED]),
])
def test_validate_duration_minutes(duration_minutes, expected_value, expected_errors):
    typed_value, errors = validate_duration_minutes(duration_minutes)
    assert typed_value == expected_value
    assert errors == expected_errors



@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"category": "Study", "description": "Algorithms", "duration_minutes": "45"},
        {"category": "Study", "description": "Algorithms", "duration_minutes": 45},
        {}
    ),
    (
        {"category": "", "description": "a" * 201, "duration_minutes": "-5"},
        {},
        {
            "category": [CATEGORY_REQUIRED],
            "description": [DESCRIPTION_LENGTH],
            "duration_minutes": [DURATION_POSITIVE]
        }
    )
])
def test_validate_time_entry(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_time_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors
