from pydantic import Field, field_validator, BaseModel
from app.shared.schemas import APIReadSchema, APISchema
from pycountry import countries
from datetime import date
from app.modules.auth.models import (
    NAME_MAX_LENGTH,
    NAME_REGEX,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_REGEX,
    HourCycleEnum,
    SexEnum,
    UnitSystemEnum,
)

from zoneinfo import available_timezones
VALID_TIMEZONES = available_timezones()

def validate_iana_timezone(v: str | None) -> str:
    if v not in VALID_TIMEZONES:
        raise ValueError("Invalid timezone")
    return v


class UserRegister(BaseModel):
    username: str = Field(min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH, pattern=USERNAME_REGEX)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    name: str | None = Field(default=None, max_length=NAME_MAX_LENGTH, pattern=NAME_REGEX)
    timezone: str # from JS resolvedOptions()
    csrf_token: str

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        return validate_iana_timezone(v)
    
    @field_validator("name", mode="before")
    @classmethod
    def convert_empty_str_to_none(cls, v: str | None) -> str | None:
        return None if v == "" else v


class UserPatch(APISchema):
    name: str | None = Field(default=None, max_length=NAME_MAX_LENGTH, pattern=NAME_REGEX)
    timezone: str | None = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        if v is None:
            raise ValueError("Timezone cannot be cleared")
        return validate_iana_timezone(v)

    @field_validator("name", mode="before")
    @classmethod
    def convert_empty_str_to_none(cls, v: str | None) -> str | None:
        return None if v == "" else v


BIRTH_DATE_RANGE_START = date(1900, 12, 31)

class UserProfilePatch(APISchema):
    city: str | None = Field(None, max_length=200)
    state: str | None = Field(None, max_length=2) # TODO: scrap or not?
    country: str | None = None
    unit_system: UnitSystemEnum | None = None
    hour_cycle: HourCycleEnum | None = None
    sex: SexEnum | None = None
    birth_date: date | None = None
    height_cm: int | None = Field(None, gt=0, lt=300)

    @field_validator("birth_date")
    @classmethod
    def reject_invalid_range(cls, v: date | None) -> date | None:
        if v is not None and (v <= BIRTH_DATE_RANGE_START or v >= date.today()):
            raise ValueError("Birth date must be after 1900-12-31 and before today")
        return v


    ### TODO: can't be null? tf?
    @field_validator("unit_system", "hour_cycle")
    @classmethod
    def reject_explicit_nulls(cls, v: str | None) -> str:
        if v is None:
            raise ValueError("Field cannot be null")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.upper()
        if countries.get(alpha_2=v) is None:
            raise ValueError(f"Unknown country code: {v}")
        return v


class UserProfileRead(APIReadSchema):
    city: str | None
    country: str | None
    unit_system: UnitSystemEnum
    hour_cycle: HourCycleEnum
    sex: SexEnum | None
    birth_date: date | None
    height_cm: int | None
    latitude: float | None
    longitude: float | None


class UserGoalsPatch(APISchema):
    weight: float | None = Field(None, gt=0)
    calories: int | None = Field(None, gt=0)
    steps: int | None = Field(None, gt=0)
    sleep_duration_minutes: int | None = Field(None, gt=0)
    protein: int | None = Field(None, gt=0)
    fat: int | None = Field(None, gt=0)
    carbs: int | None = Field(None, gt=0)
    potassium: int | None = Field(None, gt=0)
    sodium: int | None = Field(None, gt=0)

class UserGoalsRead(APIReadSchema):
    weight: float | None
    calories: int | None
    steps: int | None
    sleep_duration_minutes: int | None
    protein: int | None
    fat: int | None
    carbs: int | None
    potassium: int | None
    sodium: int | None


