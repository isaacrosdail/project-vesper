import pytest
from app.modules.auth.validators import *


@pytest.mark.parametrize("user_data", [
    {"username": "abc", "password": "password123", "name": "John"},
    {"username": "validuser", "password": "password123", "name": ""},
    {"username": "valid_user123", "password": "password123", "name": ""},
    {"username": "abc123", "password": "password123", "name": ""},
    {"username": "long_but_still_valid_username", "password": "password123", "name": ""},
    {"username": "a" * 50, "password": "password123"},
    {"username": "  validuser  ", "password": "  password123  ", "name": "  John  "},
    {"username": "user123", "password": "pass@word!", "name": "John Doe"},
    {"username": "user_name", "password": "12345678"},
    {"username": "testuser", "password": "a" * 50},
])
def test_validate_user_success(user_data):
    assert validate_user(user_data) == []

@pytest.mark.parametrize("user_data,expected_errors", [
    ({"username": "", "password": "password123"}, [USERNAME_REQUIRED]),
    ({"username": "   ", "password": "password123"}, [USERNAME_REQUIRED]),
    ({"username": "ab", "password": "password123"}, [USERNAME_CHARSET]),
    ({"username": "a" * 51, "password": "password123"}, [USERNAME_CHARSET]),
    ({"username": "validuser", "password": "        "}, [PASSWORD_REQUIRED]),
    ({"username": "user name", "password": "password123"}, [USERNAME_CHARSET]),
    ({"username": "weird!name", "password": "password123"}, [USERNAME_CHARSET]),
    ({"username": "dollar$name", "password": "password123"}, [USERNAME_CHARSET]),
    ({"username": "validuser", "password": ""}, [PASSWORD_REQUIRED]),
    ({"username": "validuser", "password": "1234567"}, [PASSWORD_LENGTH]),
    ({"username": "validuser", "password": "a" * 51}, [PASSWORD_LENGTH]),
    ({"username": "validuser", "password": "password123", "name": "a" * 51}, [NAME_CHARSET]),
    ({"username": "validuser", "password": "password123", "name": "John@"}, [NAME_CHARSET]),
    ({"username": "", "password": ""}, [USERNAME_REQUIRED, PASSWORD_REQUIRED]),
])
def test_validate_user_errors(user_data, expected_errors):
    errors = validate_user(user_data)
    assert set(errors) == set(expected_errors)