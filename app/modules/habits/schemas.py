
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator, AwareDatetime

from app.shared.schemas import TargetCreate, TargetRead
from app.modules.habits.models import (
    HABIT_NAME_MAX_LENGTH,
    HabitTypeEnum,
)
from app.shared.schemas import APIReadSchema, APISchema, PillarRead


class HabitPatch(APISchema):
    name: str | None = Field(None, min_length=1, max_length=HABIT_NAME_MAX_LENGTH)
    weekly_frequency: int | None = Field(default=None, ge=1, le=7)
    pillar_ids: list[int] | None = None
    units: str | None = Field(None, max_length=50)
    target: TargetCreate | None = None

    @field_validator("name", "weekly_frequency")
    @classmethod
    def reject_explicit_nulls(cls, v: Any | None) -> Any | None:
        if v is None:
            raise ValueError(f"Field cannot be none")
        return v


class HabitCreateBase(APISchema):
    name: str = Field(min_length=1, max_length=HABIT_NAME_MAX_LENGTH)
    weekly_frequency: int = Field(ge=1, le=7)
    pillar_ids: list[int] = []

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
    weekly_frequency: int
    created_at: datetime
    pillars: list[PillarRead]
    subtype: Literal['habits']
    type: HabitTypeEnum
    units: str | None
    target: TargetRead | None


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

class HabitOverviewItemRead(HabitRead):
    completed_today: bool
    streak_count: int
    data: list[HabitDayRead]


