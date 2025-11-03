from datetime import date
import sys
import pytest

from app.modules.time_tracking.validators import *
from app.shared.validators import DATE_REQUIRED


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
            "category": [CATEGORY_REQUIRED],
            "description": [DESCRIPTION_LENGTH],
            "entry_date": [DATE_REQUIRED]
        }
    )
])
def test_validate_time_entry(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_time_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors
