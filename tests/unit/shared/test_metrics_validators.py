import pytest
from app.modules.metrics.validators import *


@pytest.mark.parametrize("weight, expected", [
    ("70.5", []),
    ("0.1", []),
    ("0", [WEIGHT_POSITIVE]),
    ("-5", [WEIGHT_POSITIVE]),
    ("not_a_number", [WEIGHT_INVALID]),
    ("123.456", [WEIGHT_INVALID]),  # Too many decimals
])
def test_validate_weight(weight, expected):
    assert validate_weight(weight) == expected

@pytest.mark.parametrize("steps, expected", [
    ("10000", []),
    ("0", []),
    ("-100", [STEPS_NEGATIVE]),
    ("not_a_number", [STEPS_INVALID]),
    ("10.5", [STEPS_INVALID]),  # Float not allowed
])
def test_validate_steps(steps, expected):
    assert validate_steps(steps) == expected

@pytest.mark.parametrize("calories, expected", [
    ("2000", []),
    ("0", []),
    ("-200", [CALORIES_NEGATIVE]),
    ("not_a_number", [CALORIES_INVALID]),
    ("100.5", [CALORIES_INVALID]),  # Float not allowed
])
def test_validate_calories(calories, expected):
    assert validate_calories(calories) == expected

@pytest.mark.skip(reason="Wake time validation not implemented yet")
def test_validate_wake_time(): ...

@pytest.mark.skip(reason="Sleep time validation not implemented yet")
def test_validate_sleep_time(): ...


@pytest.mark.parametrize("data, expected", [
    ({"weight": "75.0", "steps": "9000", "calories": "1800"}, {})
])
def test_validate_daily_entry_valid(data, expected):
    assert validate_daily_entry(data) == expected


@pytest.mark.parametrize("data, expected", [
    ({"weight": "0", "steps": "-10", "calories": "not_number"},
    {
        "weight": [WEIGHT_POSITIVE],
        "steps": [STEPS_NEGATIVE],
        "calories": [CALORIES_INVALID]
    })
])
def test_validate_daily_entry_combined_errors(data, expected):
    assert validate_daily_entry(data) == expected
