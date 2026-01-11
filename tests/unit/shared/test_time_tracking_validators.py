from datetime import date

import pytest

from app.modules.time_tracking import validators as v


@pytest.mark.parametrize("category, expected_value, expected_errors", [
    ("Programming", "Programming", []),
    ("", None, [v.CATEGORY_REQUIRED]),
    ("a" * 51, None, [v.CATEGORY_TOO_LONG]),
])
def test_validate_category(category, expected_value, expected_errors):
    typed_value, errors = v.validate_category(category)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("description, expected_value, expected_errors", [
    (None, None, []),
    ("", None, []),
    ("Some description", "Some description", []),
    ("a" * 201, None, [v.DESCRIPTION_LENGTH]),
])
def test_validate_description(description, expected_value, expected_errors):
    typed_value, errors = v.validate_description(description)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"entry_date": "2025-10-23","category": "Study", "description": "Algorithms", "started_at": "12:00", "ended_at": "13:40"},
        {"entry_date": date(2025, 10, 23), "category": "Study", "description": "Algorithms", "started_at": "12:00", "ended_at": "13:40"},
        {}
    ),
    (
        {"category": "", "description": "a" * 201, "started_at": "12:00", "ended_at": "13:20"},
        {"started_at": "12:00", "ended_at": "13:20"},
        {
            "category": [v.CATEGORY_REQUIRED],
            "description": [v.DESCRIPTION_LENGTH],
            "entry_date": [v.DATE_REQUIRED]
        }
    )
])
def test_validate_time_entry(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_time_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors
