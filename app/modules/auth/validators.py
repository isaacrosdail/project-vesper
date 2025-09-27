
import regex

from app.modules.auth.models import UserRoleEnum, UserLangEnum
from app.modules.auth.constants import *
from app.shared.validators import validate_enum

def validate_username(username: str) -> list[str]:
    errors = []
    if not username:
        errors.append(USERNAME_REQUIRED)
    elif not regex.match(USERNAME_REGEX, username):
        errors.append(USERNAME_CHARSET)
    return errors

def validate_password(password: str) -> list[str]:
    errors = []
    if not password:
        errors.append(PASSWORD_REQUIRED)
    elif not regex.match(PASSWORD_REGEX, password):
        errors.append(PASSWORD_LENGTH)
    return errors

def validate_name(name: str) -> list[str]:
    errors = []
    if name and not regex.match(NAME_REGEX, name):
        errors.append(NAME_CHARSET)
    return errors

def validate_role(role: str) -> list[str]:
    return validate_enum(role, UserRoleEnum, USERROLE_REQUIRED, USERROLE_INVALID)

def validate_lang(lang: str) -> list[str]:
    return validate_enum(lang, UserLangEnum, USERLANG_REQUIRED, USERLANG_INVALID)


VALIDATION_FUNCS = {
    "username": validate_username,
    "password": validate_password,
    "role": validate_role,
    "lang": validate_lang
}

def validate_user(data: dict) -> dict[str, list[str]]:
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
    return errors