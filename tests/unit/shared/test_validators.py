
from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.shared.validators import *


# Trying out Hypothesis
# @given(
#         value=st.text(),
#         precision=st.integers(1, 10),
#         scale=st.integers(0, 5),
#     )
# def test_validate_numeric_never_crashes(value, precision, scale):
#     is_valid, error_type = validate_numeric(value, precision, scale)
#     assert isinstance(is_valid, bool)
#     assert (error_type is None) or isinstance(error_type, str)


@pytest.mark.parametrize("date_str, expected_value, expected_errors", [
    ("2025-09-20", date(2025, 9, 20), []),
    ("", None, [DATE_REQUIRED]),
    ("-not-date", None, [DATE_INVALID]),
])
def test_validate_date_iso(date_str, expected_value, expected_errors):
    typed_value, errors = validate_date_iso(date_str)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("time_str, expected_value, expected_errors", [
    ("22:00", "22:00", []),
    ("00:00", "00:00", []),
    ("09:05", "09:05", []),
    (None, None, [TIME_HHMM_REQUIRED]),
    ("9:05", None, [TIME_HHMM_INVALID]),
    ("12-14", None, [TIME_HHMM_INVALID]),
    ("99:99", None, [TIME_HHMM_INVALID_RANGE]),
    ("24:00", None, [TIME_HHMM_INVALID_RANGE]),
])
def test_validate_time_hhmm(time_str, expected_value, expected_errors):
    typed_value, errors = validate_time_hhmm(time_str)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("value, minimum, strict_min, expected_valid, expected_error", [
    # No minimum check
    pytest.param("5", None, False, True, None, id="no-min-positive"),
    pytest.param("-10", None, False, True, None, id="no-min-negative"),

    # minimum=0, non-strict (>= 0)
    pytest.param("0", 0, False, True, None, id="zero-non-strict"),
    pytest.param("0.01", 0, False, True, None, id="positive-non-strict"),
    pytest.param("-0.01", 0, False, False, CONSTRAINT_VIOLATION, id="negative-non-strict"),

    # minimum=0, strict (> 0)
    pytest.param("0", 0, True, False, CONSTRAINT_VIOLATION, id="zero-strict"),
    pytest.param("0.01", 0, True, True, None, id="positive-strict"),
    pytest.param("-0.01", 0, True, False, CONSTRAINT_VIOLATION, id="negative-strict"),

    # Negative minimums
    pytest.param("-5", -10, False, True, None, id="above-neg-min"),
    pytest.param("-10", -10, False, True, None, id="at-neg-min-non-strict"),
    pytest.param("-11", -10, False, False, CONSTRAINT_VIOLATION, id="below-neg-min"),
    pytest.param("-10", -10, True, False, CONSTRAINT_VIOLATION, id="at-neg-min-strict"),
    pytest.param("-9", -10, True, True, None, id="above-neg-min-strict"),
])
def test_validate_numeric_minimum_validation(value, minimum, strict_min, expected_valid, expected_error):
    is_valid, error_type = validate_numeric(value, precision=10, scale=5, minimum=minimum, strict_min=strict_min)
    assert is_valid == expected_valid
    assert error_type == expected_error

@pytest.mark.parametrize("value, precision, scale, expected_valid, expected_error", [
    # Precision limits
    pytest.param("123", 5, 2, True, None, id=""),
    pytest.param("123456", 5, 2, False, PRECISION_EXCEEDED, id=""),

    # Scale limits
    pytest.param("123.12", 5, 2, True, None, id=""),
    pytest.param("123.123", 5, 2, False, SCALE_EXCEEDED, id=""),

    pytest.param("0.00", 5, 2, True, None, id="valid-zero"),
    pytest.param("5.", 5, 2, True, None, id=""),
    pytest.param("0.000", 5, 2, False, SCALE_EXCEEDED, id=""),
    pytest.param("12345.6", 5, 1, False, PRECISION_EXCEEDED, id=""),
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