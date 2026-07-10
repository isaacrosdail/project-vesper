
from pydantic import BaseModel, Field

from app.modules.habits.models import (
    HABIT_NAME_MAX_LENGTH,
    StatusEnum,
)


class HabitPatch(BaseModel):
    name: str | None = Field(default=None, max_length=HABIT_NAME_MAX_LENGTH)
    target_frequency: int | None = Field(default=None, gt=0)
    is_promotable: bool | None = None
    pillar_ids: list[int] | None = None


class Habit(BaseModel):
    name: str = Field(max_length=HABIT_NAME_MAX_LENGTH)
    target_frequency: int = Field(gt=0)
    is_promotable: bool = False
    pillar_ids: list[int] = []

