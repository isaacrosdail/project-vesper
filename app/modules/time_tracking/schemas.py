from datetime import date, datetime, time
from typing import Literal

from pydantic import Field

from app.modules.time_tracking.models import CATEGORY_MAX_LENGTH, DESCRIPTION_MAX_LENGTH
from app.shared.schemas import APIReadSchema, APISchema, PillarRead


class TimeEntryCreate(APISchema):
    entry_date: date
    category: str = Field(max_length=CATEGORY_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    started_at: time
    ended_at: time
    pillar_ids: list[int] = []

class TimeEntryPatch(APISchema):
    entry_date: date | None = None
    category: str | None = Field(default=None, max_length=CATEGORY_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    started_at: time | None = None
    ended_at: time | None = None
    pillar_ids: list[int] | None = None # TODO:???


class TimeEntryRead(APIReadSchema):
    id: int
    category: str
    description: str | None
    started_at: datetime
    ended_at: datetime
    duration_minutes: int
    pillars: list[PillarRead]
    created_at: datetime
    subtype: Literal['time_entries']
