
from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator, AwareDatetime

from app.modules.habits.models import (
    HABIT_NAME_MAX_LENGTH,
    StatusEnum,
)
from app.shared.schemas import APIReadSchema, APISchema, PillarRead


class HabitPatch(APISchema):
    name: str | None = Field(default=None, max_length=HABIT_NAME_MAX_LENGTH)
    target_frequency: int | None = Field(default=None, gt=0)
    is_promotable: bool | None = None
    pillar_ids: list[int] | None = None

    @field_validator("name", "target_frequency")
    @classmethod
    def reject_explicit_nulls(cls, v: Any | None) -> Any | None:
        if v is None:
            raise ValueError(f"Field cannot be none")
        return v


class HabitCreate(APISchema):
    name: str = Field(min_length=1, max_length=HABIT_NAME_MAX_LENGTH)
    target_frequency: int = Field(gt=0)
    is_promotable: bool = False
    pillar_ids: list[int] = []

class HabitRead(APIReadSchema):
    id: int
    name: str
    status: StatusEnum | None
    established_date: datetime | None
    target_frequency: int
    created_at: datetime
    is_promotable: bool
    pillars: list[PillarRead]
    subtype: Literal['habits']


class HabitCompletionCreate(APISchema):
    completed_at: AwareDatetime

class HabitCompletionRead(APIReadSchema):
    id: int
    habit_id: int
    completed_at: datetime
    created_at: datetime
    subtype: Literal['habit_completions']

class HabitCompletionProgressRead(APIReadSchema):
    completed: int
    total: int
    percent: int
