import pytest
from hypothesis import given, settings, strategies as st

from app.modules.auth.constants import *
from app.modules.auth.validators import *


# NOTE: Trying out Hypothesis
# @settings(max_examples=20)
# @given(st.text(min_size=0, max_size=5))



@pytest.mark.parametrize("username, expected_value, expected_errors", [
    ("", None, [USERNAME_REQUIRED]),
    ("ab", None, [USERNAME_CHARSET]),
    ("valid_user123", "valid_user123", []),
    ("$bad_username!", None, [USERNAME_CHARSET]),
    ("    ", None, [USERNAME_CHARSET]),
])
def test_validate_username(username, expected_value, expected_errors):
    typed_value, errors = validate_username(username)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("password, expected_value, expected_errors", [
    ("", None, [PASSWORD_REQUIRED]),
    ("short", None, [PASSWORD_INVALID]),
    ("a" * 51, None, [PASSWORD_INVALID]),
    ("validpass", "validpass", []),
])
def test_validate_password(password, expected_value, expected_errors):
    typed_value, errors = validate_password(password)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("name, expected_value, expected_errors", [
    ("", None, []),
    ("Valid Name", "Valid Name", []),
    ("J'onn-Doe", "J'onn-Doe", []),
    ("@" * 10, None, [NAME_CHARSET]),
    ("A" * 51, None, [NAME_CHARSET]),
])
def test_validate_name(name, expected_value, expected_errors):
    typed_value, errors = validate_name(name)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("role, expected_value, expected_errors", [
    ("", None, [USERROLE_REQUIRED]),
    ("ADMIN", UserRoleEnum.ADMIN, []),
    ("notarole", None, [USERROLE_INVALID]),
])
def test_validate_role(role, expected_value, expected_errors):
    typed_value, errors = validate_role(role)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("lang, expected_value, expected_errors", [
    ("", None, [USERLANG_REQUIRED]),
    ("EN", UserLangEnum.EN, []),
    ("xx", None, [USERLANG_INVALID]),
])
def test_validate_lang(lang, expected_value, expected_errors):
    typed_value, errors = validate_lang(lang)
    assert typed_value == expected_value
    assert errors == expected_errors


@pytest.mark.parametrize("data, expected_typed_data, expected_errors", [
    (
        {"username": "steve123", "password": "god12@"},
        {"username": "steve123"},
        {
            "password": [PASSWORD_INVALID]
        }
    ),
])
def test_validate_user(data, expected_typed_data, expected_errors):
    typed_data, errors = validate_user(data)
    assert typed_data == expected_typed_data
    assert errors == expected_errors