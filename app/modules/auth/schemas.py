import regex
from pydantic import BaseModel, Field, field_validator

from app.modules.auth.models import (
    NAME_CHARSET,
    NAME_MAX_LENGTH,
    NAME_REGEX,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_REGEX,
)


class UserRegister(BaseModel):
    username: str = Field(min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH, pattern=USERNAME_REGEX)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    name: str | None = Field(default=None, max_length=NAME_MAX_LENGTH, pattern=NAME_REGEX)

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        if not regex.match(USERNAME_REGEX, username):
            raise ValueError(USERNAME_CHARSET)
        return username

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str | None) -> str | None:
        if name and not regex.match(NAME_REGEX, name):
            raise ValueError(NAME_CHARSET)
        return name
