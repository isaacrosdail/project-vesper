from datetime import date, time

from pydantic import BaseModel, Field

from app.modules.time_tracking.models import CATEGORY_MAX_LENGTH, DESCRIPTION_MAX_LENGTH


class TimeEntryCreate(BaseModel):
    entry_date: date
    category: str = Field(max_length=CATEGORY_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    started_at: time
    ended_at: time
    pillar_ids: list[int] = []

class TimeEntryPatch(BaseModel):
    entry_date: date | None = None
    category: str | None = Field(default=None, max_length=CATEGORY_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    started_at: time | None = None
    ended_at: time | None = None
    pillar_ids: list[int] | None = None # ???
