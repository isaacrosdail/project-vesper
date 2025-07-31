from app.core.auth.repository import get_user_by_username
from app.core.messages import msg
from app.core.constants import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MAX_NAME_LENGTH

# Password: Needs to: exist, have min length, and ideally be complex (TODO: Enforce complexity later)
# Name: Needs to: exist, stay under max length

def validate_username(username: str, session, lang="en") -> list[str]:
    errors = []
    
    # TODO: Add pattern matching (alphanumeric), for now just check length
    if not 3 <= len(username) <= 30: # pythonic range test, drill these
        errors.append(msg("username_invalid", lang))
    # Ensure username isn't taken already
    if get_user_by_username(username, session):
        errors.append(msg("username_taken", lang))

    return errors

def validate_password(password: str, lang="en") -> list[str]:
    errors = []

    # Check length
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        errors.append(msg("password_short", lang))

    return errors

def validate_name(name: str, lang="en") -> list[str]:
    errors = []

    # Validate existent & not whitespace only
    if name:
        errors.append(msg("name_invalid")) 
    if (len(name) <= MAX_NAME_LENGTH):
        errors.append(msg("name_invalid"))

    return errors