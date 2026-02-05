from __future__ import annotations
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enum import Enum

import regex

FORMAT_ERROR = "format_error"
CONSTRAINT_VIOLATION = "constraint_violation"
PRECISION_EXCEEDED = "precision_exceeded"
SCALE_EXCEEDED = "scale_exceeded"

DATE_REQUIRED = "Required date value"
DATE_INVALID = "Invalid date format"

TIME_HHMM_INVALID = "Invalid: Time must be in HH:MM format (00:00 - 23:59)"
TIME_HHMM_INVALID_RANGE = "Invalid time range (must be in 00:00 - 23:59)"
TIME_HHMM_REQUIRED = "Time value is required"


def validate_numeric(
    value: str,
    precision: int,
    scale: int,
    minimum: int | None = None,
    *,
    strict_min: bool = False,
) -> tuple[bool, str | None]:
    """Validate numeric string against precision/scale/minimum constraints.

    Returns (is_valid, error_type). Error types: FORMAT_ERROR, CONSTRAINT_VIOLATION,
    PRECISION_EXCEEDED, SCALE_EXCEEDED.
    """

    ok, dec = parse_decimal(value)
    if not ok or dec is None:
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
    exponent = int(dec.as_tuple().exponent)
    fractional_digits = abs(exponent) if exponent < 0 else 0
    integer_digits = len(digits) - fractional_digits

    if fractional_digits > scale:
        return False, SCALE_EXCEEDED
    if integer_digits > (precision - scale):
        return False, PRECISION_EXCEEDED

    return True, None


def validate_date_iso(date_str: str | None) -> tuple[date | None, list[str]]:
    """Validate date string in YYYY-MM-DD format."""
    if not date_str:
        return (None, [DATE_REQUIRED])

    try:
        return (date.fromisoformat(date_str), [])
    except ValueError:
        return (None, [DATE_INVALID])


def validate_time_hhmm(time_str: str | None) -> tuple[str | None, list[str]]:
    """Validate time string in HH:MM format (00:00 - 23:59)."""

    if not time_str:
        return (None, [TIME_HHMM_REQUIRED])

    # 2-digits either side of ':'
    if not regex.match(r"^\d{2}:\d{2}$", time_str):
        return (None, [TIME_HHMM_INVALID])

    try:
        hours, minutes = map(int, time_str.split(":"))

        if not (0 <= hours <= 23 and 0 <= minutes <= 59):  # noqa: PLR2004
            return (None, [TIME_HHMM_INVALID_RANGE])

    except ValueError:
        return (None, [TIME_HHMM_INVALID])

    return (time_str, [])


def validate_int(
    int_value: str, invalid_error: str
) -> tuple[int | None, list[str]]:
    """Coerce string to positive int. Does not handle None/empty."""
    try:
        typed_value = int(int_value)
        if typed_value <= 0:
            return (None, [invalid_error])
        return (typed_value, [])
    except (ValueError, TypeError):
        return (None, [invalid_error])

def validate_required_int(
    id_value: str | None, invalid_error: str, required_error: str
) -> tuple[int | None, list[str]]:
    """Validate required integer ID field. Returns error if missing or invalid."""
    if not id_value:
        return (None, [required_error])
    return validate_int(id_value, invalid_error)

def validate_optional_int(
    id_value: str | None, invalid_error: str
) -> tuple[int | None, list[str]]:
    """Validate optional integer ID field. Returns (None, []) if missing."""
    if not id_value:
        return (None, [])
    return validate_int(id_value, invalid_error)


def validate_string(
    value: str | None, max_length: int | None, length_error: str
) -> tuple[str | None, list[str]]:
    """Validate & normalize a string value.
    - strips whitespace
    - converts "" -> None
    - Checks max length if provided
    Does not handle optional/required logic.
    """
    if not value:
        return (None, [])

    stripped = value.strip()
    if not stripped:
        return (None, [])

    if max_length and len(stripped) > max_length:
        return (None, [length_error])

    return (stripped, [])


def validate_required_string(
    value: str | None,
    max_length: int | None,
    required_error: str,
    length_error: str
) -> tuple[str | None, list[str]]:
    """Required string with optional max length."""
    if not value or not value.strip():
        return (None, [required_error])

    return validate_string(value, max_length, length_error)


def validate_optional_string(
    value: str | None, 
    max_length: int | None, 
    length_error: str
) -> tuple[str | None, list[str]]:
    """Optional string with optional max length. Returns (None, []) if missing."""
    if not value:
        return (None, [])
    
    return validate_string(value, max_length, length_error)



def validate_enum(
    value: str, enum_class: type[Enum], invalid_error: str
) -> tuple[Enum | None, list[str]]:
    """
    Validate enum value, normalizing to uppercase.
    Returns enum member if valid, None otherwise.
    """
    try:
        enum_member = enum_class[value.upper()]
        return (enum_member, [])
    except KeyError:
        return (None, [invalid_error])

def validate_required_enum(
    value: str | None,
    enum_class: type[Enum],
    invalid_error: str,
    required_error: str
) -> tuple[Enum | None, list[str]]:
    if not value:
        return (None, [required_error])
    return validate_enum(value, enum_class, invalid_error)

def validate_optional_enum(
    value: str | None,
    enum_class: type[Enum],
    invalid_error: str,
) -> tuple[Enum | None, list[str]]:
    if not value:
        return (None, [])
    return validate_enum(value, enum_class, invalid_error)


def parse_decimal(value: float | str) -> tuple[bool, Decimal | None]:
    """Parse value to Decimal, rejecting inf/NaN. Returns (ok, decimal_value)."""
    try:
        # str() avoids float rounding issues & ensures proper parsing
        dec = Decimal(str(value))
    except InvalidOperation:
        return False, None

    if dec.is_infinite() or dec.is_nan():
        return False, None

    return True, dec


# NOTE: add validate_str, with params like ALLOWED_CHARSET, etc?
