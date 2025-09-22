import pytest
from app.modules.metrics.validators import validate_daily_entry

# Metrics constants
WEIGHT_POSITIVE = "Weight must be greater than 0"
WEIGHT_INVALID = "Weight must be a valid number"
STEPS_NEGATIVE = "Steps cannot be negative"
STEPS_INVALID = "Steps must be a valid whole number"
CALORIES_POSITIVE = "Calories must be greater than 0"
CALORIES_INVALID = "Calories must be a valid whole number"

@pytest.mark.parametrize("entry_data", [
    # Empty entry (all optional)
    {},
    # Single fields
    {"weight": "70.5"},
    {"steps": "10000"},
    {"calories": "2000"},
    # Multiple fields
    {"weight": "65.2", "steps": "8500", "calories": "1800"},
    # Edge cases
    {"weight": "0.1", "steps": "0", "calories": "1"},  # Minimal values
    {"weight": "200", "steps": "50000", "calories": "5000"},  # Large values
])
def test_validate_daily_entry_success(entry_data):
    assert validate_daily_entry(entry_data) == []

@pytest.mark.parametrize("entry_data,expected_errors", [
    # Invalid weight
    ({"weight": "0"}, [WEIGHT_POSITIVE]),
    ({"weight": "-5"}, [WEIGHT_POSITIVE]),
    ({"weight": "not_a_number"}, [WEIGHT_INVALID]),
    
    # Invalid steps
    ({"steps": "-100"}, [STEPS_NEGATIVE]),
    ({"steps": "not_a_number"}, [STEPS_INVALID]),
    ({"steps": "10.5"}, [STEPS_INVALID]),  # Should be whole number
    
    # Invalid calories
    ({"calories": "0"}, [CALORIES_POSITIVE]),
    ({"calories": "-200"}, [CALORIES_POSITIVE]),
    ({"calories": "not_a_number"}, [CALORIES_INVALID]),
    ({"calories": "100.5"}, [CALORIES_INVALID]),  # Should be whole number
])
def test_validate_daily_entry_errors(entry_data, expected_errors):
    errors = validate_daily_entry(entry_data)
    assert set(errors) == set(expected_errors)