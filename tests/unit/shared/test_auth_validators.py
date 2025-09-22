import pytest
from app.modules.auth.validators import validate_user

# Error message constants
USERNAME_REQUIRED = "Username is required"
USERNAME_LENGTH = "Username must be 3-50 characters"
PASSWORD_REQUIRED = "Password is required"
PASSWORD_LENGTH = "Password must be 8-50 characters"
NAME_LENGTH = "Name must be under 50 characters"


@pytest.mark.parametrize("user_data", [
    {"username": "abc", "password": "password123", "name": "John"},
    {"username": "validuser", "password": "password123", "name": ""},
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
    ({"username": "ab", "password": "password123"}, [USERNAME_LENGTH]),
    ({"username": "a" * 51, "password": "password123"}, [USERNAME_LENGTH]),
    ({"username": "validuser", "password": ""}, [PASSWORD_REQUIRED]),
    ({"username": "validuser", "password": "1234567"}, [PASSWORD_LENGTH]),
    ({"username": "validuser", "password": "a" * 51}, [PASSWORD_LENGTH]),
    ({"username": "validuser", "password": "password123", "name": "a" * 51}, [NAME_LENGTH]),
    ({"username": "", "password": ""}, [USERNAME_REQUIRED, PASSWORD_REQUIRED]),
])
def test_validate_user_errors(user_data, expected_errors):
    errors = validate_user(user_data)
    for expected_error in expected_errors:
        assert expected_error in errors