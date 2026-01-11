from datetime import date

import pytest

from app.modules.metrics import validators as v


@pytest.mark.parametrize("weight, expected_value, expected_errors", [
    ("70.5", 70.5, []),
    ("0.1", 0.1, []),
    ("0", None, [v.WEIGHT_POSITIVE]),
    ("-5", None, [v.WEIGHT_POSITIVE]),
    ("not_a_number", None, [v.WEIGHT_INVALID]),
    ("123.456", None, [v.WEIGHT_INVALID]),  # Too many decimals
])
def test_validate_weight(weight, expected_value, expected_errors):
    typed_value, errors = v.validate_weight(weight)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("steps, expected_value, expected_errors", [
    ("10000", 10000, []),
    ("0", 0, []),
    ("-100", None, [v.STEPS_NEGATIVE]),
    ("not_a_number", None, [v.STEPS_INVALID]),
    ("10.5", None, [v.STEPS_INVALID]),  # Float not allowed
])
def test_validate_steps(steps, expected_value, expected_errors):
    typed_value, errors = v.validate_steps(steps)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("calories, expected_value, expected_errors", [
    ("2000", 2000, []),
    ("0", 0, []),
    ("-200", None, [v.CALORIES_NEGATIVE]),
    ("not_a_number", None, [v.CALORIES_INVALID]),
    ("100.5", None, [v.CALORIES_INVALID]),  # Float not allowed
])
def test_validate_calories(calories, expected_value, expected_errors):
    typed_value, errors = v.validate_calories(calories)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("time_str, expected_value, expected_errors", [
    ("03:34", "03:34", []),
    (None, None, []),
    ("garbage", None, [v.TIME_HHMM_INVALID]),
    ("12:34:23", None, [v.TIME_HHMM_INVALID]),
    ("12", None, [v.TIME_HHMM_INVALID]),
    ("1a:4b", None, [v.TIME_HHMM_INVALID]),
    # Range issues
    ("25:34", None, [v.TIME_HHMM_INVALID_RANGE]),
    ("22:78", None, [v.TIME_HHMM_INVALID_RANGE]),
    ("-1:30", None, [v.TIME_HHMM_INVALID]),
    ("26:89", None, [v.TIME_HHMM_INVALID_RANGE])
])
def test_validate_time_hhmm_format(time_str, expected_value, expected_errors):
    typed_value, errors = v.validate_time_hhmm_format(time_str)
    assert typed_value == expected_value
    assert set(errors) == set(expected_errors)


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"entry_date": "2025-10-23", "weight": "75.0", "steps": "9000", "calories": "1800"},
        {"entry_date": date(2025, 10, 23), "weight": 75.0, "steps": 9000, "calories": 1800},
        {}
    )
])
def test_validate_daily_entry_valid(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_daily_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"entry_date": "2025-10-23", "weight": "0", "steps": "-10", "calories": "not_number"},
        {"entry_date": date(2025, 10, 23)}, # typed_data returned empty when there are errors
        {
            "weight": [v.WEIGHT_POSITIVE],
            "steps": [v.STEPS_NEGATIVE],
            "calories": [v.CALORIES_INVALID]
        }
    )
])
def test_validate_daily_entry_combined_errors(data, expected_typed_data, expected_errors):
    typed_data, errors = v.validate_daily_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors
