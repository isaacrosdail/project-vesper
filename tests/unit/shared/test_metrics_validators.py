import pytest

from app.modules.metrics.validators import *


@pytest.mark.parametrize("weight, expected_value, expected_errors", [
    ("70.5", 70.5, []),
    ("0.1", 0.1, []),
    ("0", None, [WEIGHT_POSITIVE]),
    ("-5", None, [WEIGHT_POSITIVE]),
    ("not_a_number", None, [WEIGHT_INVALID]),
    ("123.456", None, [WEIGHT_INVALID]),  # Too many decimals
])
def test_validate_weight(weight, expected_value, expected_errors):
    typed_value, errors = validate_weight(weight)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("steps, expected_value, expected_errors", [
    ("10000", 10000, []),
    ("0", 0, []),
    ("-100", None, [STEPS_NEGATIVE]),
    ("not_a_number", None, [STEPS_INVALID]),
    ("10.5", None, [STEPS_INVALID]),  # Float not allowed
])
def test_validate_steps(steps, expected_value, expected_errors):
    typed_value, errors = validate_steps(steps)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("calories, expected_value, expected_errors", [
    ("2000", 2000, []),
    ("0", 0, []),
    ("-200", None, [CALORIES_NEGATIVE]),
    ("not_a_number", None, [CALORIES_INVALID]),
    ("100.5", None, [CALORIES_INVALID]),  # Float not allowed
])
def test_validate_calories(calories, expected_value, expected_errors):
    typed_value, errors = validate_calories(calories)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("time_str, expected_value, expected_errors", [
    ("03:34", "03:34", []),
    (None, None, []),
    ("garbage", None, [TIME_HHMM_INVALID]),
    ("12:34:23", None, [TIME_HHMM_INVALID]),
    ("12", None, [TIME_HHMM_INVALID]),
    ("1a:4b", None, [TIME_HHMM_DIGITS]),
    # Range issues
    ("25:34", None, [TIME_HHMM_HOUR]),
    ("22:78", None, [TIME_HHMM_MINUTE]),
    ("-1:30", None, [TIME_HHMM_DIGITS]),
    ("26:89", None, [TIME_HHMM_HOUR, TIME_HHMM_MINUTE])
])
def test_validate_time_hhmm_format(time_str, expected_value, expected_errors):
    typed_value, errors = validate_time_hhmm_format(time_str)
    assert typed_value == expected_value
    assert set(errors) == set(expected_errors)


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"weight": "75.0", "steps": "9000", "calories": "1800"},
        {"weight": 75.0, "steps": 9000, "calories": 1800},
        {}
    )
])
def test_validate_daily_entry_valid(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_daily_entry(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"weight": "0", "steps": "-10", "calories": "not_number"},
        {}, # typed_data returned empty when there are errors
        {
            "weight": [WEIGHT_POSITIVE],
            "steps": [STEPS_NEGATIVE],
            "calories": [CALORIES_INVALID]
        }
    )
])
def test_validate_daily_entry_combined_errors(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_daily_entry(data) 
    assert typed_data == expected_typed_data
    assert errors == expected_errors
