import pytest

from hypothesis import given, strategies as st

from app.modules.auth.validators import *
from app.modules.auth.constants import *


# NOTE: Trying out Hypothesis
@given(st.text(min_size=0, max_size=5))
def test_validate_lang_random(lang):
    result = validate_lang(lang)

    # Invariants we expect, regardless of input:
    if lang == "":
        assert result == [USERLANG_REQUIRED]
    elif lang == "en" or lang == "de":
        assert result == []
    else:
        assert result == [USERLANG_INVALID]


@pytest.mark.parametrize("username, expected", [
    ("", [USERNAME_REQUIRED]),
    ("ab", [USERNAME_CHARSET]),
    ("valid_user123", []),
    ("$bad_username!", [USERNAME_CHARSET]),
    ("    ", [USERNAME_CHARSET]),
])
def test_validate_username(username, expected):
    errors = validate_username(username)
    assert set(errors) == set(expected)

@pytest.mark.parametrize("password, expected", [
    ("", [PASSWORD_REQUIRED]),
    ("short", [PASSWORD_LENGTH]),
    ("a" * 51, [PASSWORD_LENGTH]),
    ("validpass", []),
])
def test_validate_password(password, expected):
    assert validate_password(password) == expected

@pytest.mark.parametrize("name, expected", [
    ("", []),
    ("Valid Name", []),
    ("J'onn-Doe", []),
    ("@" * 10, [NAME_CHARSET]),
    ("A" * 51, [NAME_CHARSET]),
])
def test_validate_name(name, expected):
    assert validate_name(name) == expected

@pytest.mark.parametrize("role, expected", [
    ("", [USERROLE_REQUIRED]),
    ("ADMIN", []),
    ("notarole", [USERROLE_INVALID]),
])
def test_validate_role(role, expected):
    assert validate_role(role) == expected

@pytest.mark.parametrize("lang, expected", [
    ("", [USERLANG_REQUIRED]),
    ("en", []),
    ("xx", [USERLANG_INVALID]),
])
def test_validate_lang(lang, expected):
    assert validate_lang(lang) == expected