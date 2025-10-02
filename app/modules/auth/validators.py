
from typing import Any

import regex

from app.modules.auth.constants import *
from app.modules.auth.models import UserLangEnum, UserRoleEnum
from app.shared.validators import validate_enum


def validate_username(username: str) -> tuple[str | None, list[str]]:
    """Required. String, 3-30 chars, Unicode letters/numbers/underscores."""
    if not username:
        return (None, [USERNAME_REQUIRED])
    if not regex.match(USERNAME_REGEX, username):
        return (None, [USERNAME_CHARSET])

    return (username, [])


def validate_password(password: str) -> tuple[str | None, list[str]]:
    """Required. String, 8-50 chars."""
    if not password:
        return (None, [PASSWORD_REQUIRED])
    if not regex.match(PASSWORD_REGEX, password):
        return (None, [PASSWORD_INVALID])

    return (password, [])


def validate_name(name: str) -> tuple[str | None, list[str]]:
    """Optional. String, 1-50 chars, Unicode letters/spaces/apostrophes/hyphens."""
    if not name:
        return (None, [])
    if not regex.match(NAME_REGEX, name):
        return (None, [NAME_CHARSET])

    return (name, [])


def validate_role(role: str) -> tuple[Any, list[str]]:
    """Required. Valid UserRoleEnum value."""
    return validate_enum(role, UserRoleEnum, USERROLE_REQUIRED, USERROLE_INVALID)


def validate_lang(lang: str) -> tuple[Any, list[str]]:
    """Required. Valid UserLangEnum value."""
    return validate_enum(lang, UserLangEnum, USERLANG_REQUIRED, USERLANG_INVALID)


VALIDATION_FUNCS = {
    "username": validate_username,
    "password": validate_password,
    "role": validate_role,
    "lang": validate_lang
}

def validate_user(data: dict) -> tuple[dict, dict[str, list[str]]]:
    typed_data = {}
    errors = {}

    for field, func in VALIDATION_FUNCS.items():
        value = data.get(field)
        typed_value, field_errors = func(value)
        if field_errors:
            errors[field] = field_errors
        elif typed_value is not None:
            typed_data[field] = typed_value

    return (typed_data, errors)