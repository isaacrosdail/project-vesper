
from datetime import date, datetime
from typing import Annotated, Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from app.modules.habits.models import (
    HABIT_NAME_MAX_LENGTH,
    HabitTypeEnum,
    ScheduleTypeEnum,
)
from app.shared.schemas import (
    APIReadSchema,
    APISchema,
    PillarRead,
    TargetCreate,
    TargetRead,
)

PARAM_BY_MODE = {
    ScheduleTypeEnum.FREQUENCY: "weekly_frequency",
    ScheduleTypeEnum.WEEKLY: "scheduled_days",
    ScheduleTypeEnum.MONTHLY: "monthly_days",
    ScheduleTypeEnum.INTERVAL: "interval_days",
}

class HabitPatch(APISchema):
    name: str | None = Field(None, min_length=1, max_length=HABIT_NAME_MAX_LENGTH)
    pillar_ids: list[int] | None = None
    units: str | None = Field(None, max_length=50)
    target: TargetCreate | None = None

    schedule_type: ScheduleTypeEnum | None = None
    weekly_frequency: int | None = Field(None, ge=1, le=7)       # frequency type
    scheduled_days: list[Annotated[int, Field(ge=1, le=7)]] | None = Field(None, min_length=1) # weekly type
    monthly_days: list[int] | None = Field(None, min_length=1)   # monthly type
    interval_days: int | None = Field(None, ge=1)                # interval type
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("name")
    @classmethod
    def reject_explicit_nulls(cls, v: Any | None) -> Any | None:
        if v is None:
            raise ValueError("Field cannot be none")
        return v

    @field_validator("monthly_days")
    @classmethod
    def validate_monthly_days(cls, v: list[int] | None) -> Any:
        if v is None:
            return None
        if any(not (e == -1 or 1 <= e <= 31) for e in v):
            raise ValueError("no dude stahpp")
        return v

    @field_validator("scheduled_days", "monthly_days")
    @classmethod
    def sort_dedupe(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return None
        return sorted(set(v))

    @model_validator(mode="after")
    def validate_schedule_type_pair(self) -> Self:
        if self.schedule_type is None:
            field = [n for n in PARAM_BY_MODE.values() if getattr(self, n) is not None]
            if field:
                raise ValueError(f"Schedule params sent without schedule_type: {field}")
            return self
        chosen = PARAM_BY_MODE[self.schedule_type]
        for name in PARAM_BY_MODE.values():
            if (getattr(self, name) is not None) != (name == chosen):
                raise ValueError(f"Invalid key for {self.schedule_type} included: '{name}'")
        return self

class HabitCreateBase(APISchema):
    name: str = Field(min_length=1, max_length=HABIT_NAME_MAX_LENGTH)
    pillar_ids: list[int] = []
    schedule_type: ScheduleTypeEnum
    weekly_frequency: int | None = Field(None, ge=1, le=7)       # frequency type
    scheduled_days: list[Annotated[int, Field(ge=1, le=7)]] | None = Field(None, min_length=1) # weekly type
    monthly_days: list[int] | None = Field(None, min_length=1)   # monthly type
    interval_days: int | None = Field(None, ge=1)                # interval type
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_end_after_start_date(self) -> Self:
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise ValueError("End date must come after start date")
        return self

    @field_validator("monthly_days")
    @classmethod
    def validate_monthly_days(cls, v: list[int] | None) -> Any:
        if v is None:
            return None
        if any(not (e == -1 or 1 <= e <= 31) for e in v):
            raise ValueError("no dude stahpp")
        return v

    @field_validator("scheduled_days", "monthly_days")
    @classmethod
    def sort_dedupe(cls, v: list[int] | None) -> list[int] | None:
        if v is None:
            return None
        return sorted(set(v))

    @model_validator(mode="after")
    def validate_schedule_type_pair(self) -> Self:
        chosen = PARAM_BY_MODE[self.schedule_type]
        for name in PARAM_BY_MODE.values():
            if (getattr(self, name) is not None) != (name == chosen):
                raise ValueError(f"Invalid key for {self.schedule_type} included: '{name}'")
        return self

class BinaryHabitCreate(HabitCreateBase):
    type: Literal[HabitTypeEnum.BINARY]

class DurationHabitCreate(HabitCreateBase):
    type: Literal[HabitTypeEnum.DURATION]
    target: TargetCreate | None = None

class NumericHabitCreate(HabitCreateBase):
    type: Literal[HabitTypeEnum.NUMERIC_VALUE]
    units: str | None = Field(default=None, max_length=50)
    target: TargetCreate | None = None

HabitCreate = Annotated[BinaryHabitCreate | DurationHabitCreate | NumericHabitCreate, Field(discriminator="type")]


class HabitRead(APIReadSchema):
    id: int
    name: str
    created_at: datetime
    pillars: list[PillarRead]
    subtype: Literal['habits']
    type: HabitTypeEnum
    units: str | None
    target: TargetRead | None
    schedule_type: ScheduleTypeEnum
    weekly_frequency: int | None
    scheduled_days: list[int] | None
    monthly_days: list[int] | None
    interval_days: int | None
    start_date: date
    end_date: date | None

class HabitCompletionCreate(APISchema):
    entry_date: date
    value: float | None

class HabitCompletionRead(APIReadSchema):
    id: int
    habit_id: int
    entry_date: date
    value: float | None
    created_at: datetime
    subtype: Literal['habit_completions']

class HabitCompletionProgressRead(APIReadSchema):
    completed: int
    total: int
    percent: int

class HabitDayRead(APIReadSchema):
    entry_date: date
    value: float | None
    target: TargetRead | None
    satisfied: bool

class HabitOverviewItemRead(HabitRead):
    completed_today: bool
    streak_count: int
    data: list[HabitDayRead]
    consistency: int | None
    week_intended: list[date] | None  # this week's intended dates; None for frequency mode

