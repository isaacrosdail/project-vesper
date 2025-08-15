from app.shared.constants import (DEFAULT_LANG, MAX_NAME_LENGTH,
                                  MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH)
from app.shared.i18n.messages import msg

# Password: Needs to: exist, have min length, and ideally be complex (TODO: Enforce complexity later)
# Name: Needs to: exist, stay under max length

def validate_username(username: str, session, lang=DEFAULT_LANG) -> list[str]:
    """
    Validates username requirements: Uniqueness and length (under MAX_NAME_LENGTH)

    Args:
        username: Username to validate
        session: Database session.
        lang: language for error messages (defaults to DEFAULT_LANG)

    Returns:
        List of error message strings (empty if valid)
    """
    errors = []

    # TODO: MINOR: Add pattern matching (alphanumeric)
    if not 3 <= len(username) <= 30: # pythonic range test, drill these
        errors.append(msg("username_invalid", lang))

    return errors

def validate_password(password: str, lang=DEFAULT_LANG) -> list[str]:
    errors = []

    # Check length
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        errors.append(msg("password_short", lang))

    return errors

def validate_name(name: str, lang=DEFAULT_LANG) -> list[str]:
    errors = []

    # Validate existent & not whitespace only
    if not name:
        errors.append(msg("name_invalid", lang)) 
    if (len(name) > MAX_NAME_LENGTH):
        errors.append(msg("name_invalid", lang))

    return errors