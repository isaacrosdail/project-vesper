
from pydantic import BaseModel, Field

from app.modules.habits.models import (
    HABIT_NAME_MAX_LENGTH,
    LC_TITLE_MAX_LENGTH,
    DifficultyEnum,
    LanguageEnum,
    LCStatusEnum,
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


class LCRecord(BaseModel):
    leetcode_id: int
    title: str | None = Field(default=None, max_length=LC_TITLE_MAX_LENGTH)
    difficulty: DifficultyEnum
    language: LanguageEnum
    status: LCStatusEnum


class LCRecordPatch(BaseModel):
    title: str | None = Field(default=None, max_length=LC_TITLE_MAX_LENGTH)
    difficulty: DifficultyEnum | None = None
    language: LanguageEnum | None = None
    status: LCStatusEnum | None = None
