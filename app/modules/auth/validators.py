
import regex

# Error message constants
USERNAME_REQUIRED = "Username is required"
USERNAME_CHARSET = "Username can only contain up to 50 characters of letters, numbers, and underscores"

PASSWORD_REQUIRED = "Password is required"
PASSWORD_LENGTH = "Password must be 8-50 characters"

NAME_CHARSET = "Name can only contain up to 50 characters of letters, spaces, apostrophes, and hyphens"

# USERNAME: 3–50 chars, Unicode letters, numbers, and underscores
USERNAME_VALID = r"^[\p{L}0-9_]{3,50}$"

# PASSWORD: 8–50 chars, any characters allowed
PASSWORD_VALID = r"^.{8,50}$"

# NAME (optional): 1–50 chars, Unicode letters plus space, apostrophe, hyphen
NAME_VALID = r"^[\p{L}' -]{1,50}$"


def validate_user(data: dict) -> list[str]:
    errors = []

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()

    if not username:
        errors.append("Username is required")
    if username and not regex.match(USERNAME_VALID, username):
        errors.append("Username can only contain up to 50 characters of letters, numbers, and underscores")


    if not password:
        errors.append("Password is required")
    if password and not regex.match(PASSWORD_VALID, password):
        errors.append("Password must be 8-50 characters")


    if name and not regex.match(NAME_VALID, name):
        errors.append("Name can only contain up to 50 characters of letters, spaces, apostrophes, and hyphens")
    
    return errors