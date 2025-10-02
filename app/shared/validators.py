import regex

from typing import Any
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


FORMAT_ERROR = 'format_error'
CONSTRAINT_VIOLATION = 'constraint_violation'
PRECISION_EXCEEDED = 'precision_exceeded'
SCALE_EXCEEDED = 'scale_exceeded'

DATE_REQUIRED = "Required date value"
DATE_INVALID = "Invalid date format"

TIME_HHMM_INVALID = "Invalid: Time must be in HH:MM format (00:00 - 23:59)"
TIME_HHMM_INVALID_RANGE = "Invalid time range (must be in 00:00 - 23:59)"
TIME_HHMM_REQUIRED = "Time value is required"


def validate_numeric(value, precision, scale, minimum=None, strict_min=False) -> tuple[bool, str | None]:
    """Validate numeric string against precision/scale/minimum constraints.
    
    Returns (is_valid, error_type). Error types: FORMAT_ERROR, CONSTRAINT_VIOLATION, 
    PRECISION_EXCEEDED, SCALE_EXCEEDED.
    """
    
    ok, dec = parse_decimal(value)
    if not ok:
        return False, FORMAT_ERROR
    
    # Cases:
    # minimum=None → no lower-bound check at all.
    # minimum=0 + strict_min=True → require dec > 0.
    # minimum=0 + strict_min=False → require dec >= 0.
    if minimum is not None:
        if strict_min and dec <= minimum:
            return False, CONSTRAINT_VIOLATION
        if not strict_min and dec < minimum:
            return False, CONSTRAINT_VIOLATION

    
    # Check precision/scale
    digits = dec.as_tuple().digits
    exponent = dec.as_tuple().exponent
    fractional_digits = abs(exponent) if exponent < 0 else 0
    integer_digits = (len(digits) - fractional_digits)

    if fractional_digits > scale:
        return False, SCALE_EXCEEDED
    if integer_digits > (precision - scale):
        return False, PRECISION_EXCEEDED

    return True, None


def validate_date_iso(date_str: str) -> tuple[date | None, list[str]]:
    """Validate date string in YYYY-MM-DD format."""
    if not date_str:
        return (None, [DATE_REQUIRED])
    
    try:
        return (datetime.strptime(date_str, "%Y-%m-%d").date(), [])
    except ValueError:
        return (None, [DATE_INVALID])


def validate_time_hhmm(time_str: str) -> tuple[str | None, list[str]]:
    """Validate time string in HH:MM format (00:00 - 23:59)."""
    
    if not time_str:
        return (None, [TIME_HHMM_REQUIRED])
    
    # Format
    if not regex.match(r'^\d{2}:\d{2}$', time_str):
        return (None, [TIME_HHMM_INVALID])
    
    # Range
    try:
        hours, minutes = map(int, time_str.split(":"))

        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return (None, [TIME_HHMM_INVALID_RANGE])

    except ValueError:
        return (None, [TIME_HHMM_INVALID])
    
    return (time_str, [])


def validate_id_field(id_value: str, required_error: str, invalid_error: str) -> tuple[int | None, list[str]]:
    # TODO: Could probably streamline/just use these outright in other validators. Need to do a condensing pass.
    if not id_value:
        return (None, [required_error])

    try:
        id_int = int(id_value)
        return (id_int, [])
    except (ValueError, TypeError):
        return (None, [invalid_error])


def validate_enum(enum_str: str, enum_cls, required_error: str, invalid_error: str) -> tuple[Any, list[str]]:
    # TODO: Could probably streamline/just use these outright in other validators. Need to do a condensing pass.
    if not enum_str:
        return (None, [required_error])
    
    try:
        enum_member = enum_cls[enum_str]
        return (enum_member, [])
    except KeyError:
        return (None, [invalid_error])


def parse_decimal(value):
    """Parse value to Decimal, rejecting inf/nan. Returns (ok, decimal_value)."""
    try:
        dec = Decimal(str(value)) # str() avoids float artifacts & ensures proper parsing?
    except InvalidOperation:
        return False, None
    
    if dec.is_infinite() or dec.is_nan():
        return False, None

    return True, dec