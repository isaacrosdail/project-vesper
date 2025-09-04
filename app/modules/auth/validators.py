from app.shared.constants import (MAX_NAME_LENGTH,
                                  MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH)

# Password: Needs to: exist, have min length, and ideally be complex (TODO: Enforce complexity later)
# Name: Needs to: exist, stay under max length

def validate_username(username: str) -> list[str]:
    """
    Validates username requirements: Uniqueness and length (under MAX_NAME_LENGTH)

    Args:
        username: Username to validate

    Returns:
        List of error message strings (empty if valid)
    """
    errors = []

    # TODO: MINOR: Add pattern matching (alphanumeric)
    if not 3 <= len(username) <= 30: # pythonic range test, drill these
        errors.append("invalid username len")

    return errors

def validate_password(password: str) -> list[str]:
    errors = []

    # Check length
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        errors.append("password too short")

    return errors

def validate_name(name: str) -> list[str]:
    errors = []

    # Validate existent & not whitespace only
    if not name:
        errors.append("name invalid") 
    if (len(name) > MAX_NAME_LENGTH):
        errors.append("name invalid")

    return errors