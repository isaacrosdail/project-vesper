
from datetime import date
import math
from decimal import Decimal
from enum import Enum

from app.shared.validators import (
    validate_int,
    validate_string,
    validate_enum,
    parse_decimal,
)


class TestEnum(Enum):
    A = "a"
    B = "b"


def test_validate_int_valid_positive():
    value, errors = validate_int("5", "err")
    assert value == 5
    assert errors == []


def test_validate_int_rejects_zero_and_negative():
    assert validate_int("0", "err")[0] is None
    assert validate_int("-1", "err")[0] is None


def test_validate_int_rejects_non_int():
    value, errors = validate_int("nope", "err")
    assert value is None
    assert errors == ["err"]


def test_validate_string_strips_and_normalizes():
    value, errors = validate_string("  hello  ", 10, "len_err")
    assert value == "hello"
    assert errors == []


def test_validate_string_empty_and_whitespace_becomes_none():
    assert validate_string("", 10, "len_err")[0] is None
    assert validate_string("   ", 10, "len_err")[0] is None


def test_validate_string_enforces_max_length():
    value, errors = validate_string("toolong", 3, "len_err")
    assert value is None
    assert errors == ["len_err"]


def test_validate_enum_accepts_case_insensitive():
    value, errors = validate_enum("a", TestEnum, "err")
    assert value == TestEnum.A
    assert errors == []


def test_validate_enum_rejects_invalid():
    value, errors = validate_enum("nope", TestEnum, "err")
    assert value is None
    assert errors == ["err"]


def test_parse_decimal_valid_str_and_float():
    ok, dec = parse_decimal("1.23")
    assert ok is True
    assert dec == Decimal("1.23")

    ok, dec = parse_decimal(1.23)
    assert ok is True
    assert isinstance(dec, Decimal)


def test_parse_decimal_rejects_nan_and_inf():
    ok, dec = parse_decimal(math.nan)
    assert ok is False
    assert dec is None

    ok, dec = parse_decimal(math.inf)
    assert ok is False
    assert dec is None
