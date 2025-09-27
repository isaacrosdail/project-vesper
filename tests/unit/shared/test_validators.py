
import pytest

from hypothesis import given, strategies as st, example

from app.shared.validators import validate_numeric, FORMAT_ERROR, CONSTRAINT_VIOLATION, PRECISION_EXCEEDED, SCALE_EXCEEDED


# NOTE: Trying out Hypothesis
@given(st.text())
@example("ban") # we can use @example to force known values for specific cases we care about
def test_validate_numeric_basic(value):
    # print(f"Trying: {repr(value)}")
    is_valid, error = validate_numeric(value, precision=5, scale=2)
    if is_valid:
        assert error is None
    else:
        assert error is not None

@pytest.mark.parametrize("value, minimum, strict_min, expected_valid, expected_error", [
    # minimum=None (no lower bound checking)
    ("5", None, False, True, None),
    ("-10", None, False, True, None),

    # minimum=0 with strict_min=False (>= 0)
    ("0", 0, False, True, None),       # zero with non-strict min of 0 should pass
    ("0.01", 0, False, True, None),
    ("-0.01", 0, False, False, CONSTRAINT_VIOLATION),

    # minimum=0 with strict_min=True (> 0)
    ("0", 0, True, False, CONSTRAINT_VIOLATION),
    ("0.01", 0, True, True, None),     # positive with strict min 0 passes
    ("-0.01", 0, True, False, CONSTRAINT_VIOLATION),

    # negative minimums with both strict modes
    ("-5", -10, False, True, None),   # -5 >= -10
    ("-10", -10, False, True, None),  # -10 >= -10
    ("-11", -10, False, False, CONSTRAINT_VIOLATION), # -11 < -10
    ("-10", -10, True, False, CONSTRAINT_VIOLATION),  # -10 <= -10 (strict)
    ("-9", -10, True, True, None),    # -9 > -10 (strict)
])
def test_validate_numeric_minimum_validation(value, minimum, strict_min, expected_valid, expected_error):
    is_valid, error_type = validate_numeric(value, precision=5, scale=5, minimum=minimum, strict_min=strict_min)
    assert is_valid == expected_valid
    assert error_type == expected_error

@pytest.mark.parametrize("value, precision, scale, expected_valid, expected_error", [
    # Precision limits
    ("12345", 5, 2, True, None),
    ("123456", 5, 2, False, PRECISION_EXCEEDED),
    ("1", 5, 2, True, None),

    # Scale limits
    ("123.12", 5, 2, True, None),
    ("123.123", 5, 2, False, SCALE_EXCEEDED),
    ("123", 5, 2, True, None),

    ("0.00", 5, 2, True, None),
    ("00.10", 5, 2, True, None),
    ("0.50", 5, 2, True, None),
    ("5.", 5, 2, True, None),
    ("0.000", 5, 2, False, SCALE_EXCEEDED),
    ("12345.6", 5, 1, False, PRECISION_EXCEEDED),
])
def test_validate_numeric_precision_scale_validation(value, precision, scale, expected_valid, expected_error):
    is_valid, error_type = validate_numeric(value, precision, scale, minimum=None, strict_min=False)
    assert is_valid == expected_valid
    assert error_type == expected_error

@pytest.mark.parametrize("value, expected_valid, expected_error", [
    ("abc", False, FORMAT_ERROR),
    ("", False, FORMAT_ERROR),
    ("12.3.4", False, FORMAT_ERROR),
    ("--5", False, FORMAT_ERROR),
    ("5-", False, FORMAT_ERROR),
])
def test_validate_numeric_invalid_inputs(value, expected_valid, expected_error):
    is_valid, error_type = validate_numeric(value, precision=5, scale=2, minimum=None, strict_min=False)
    assert is_valid == expected_valid
    assert error_type == expected_error