
from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.modules.tasks.models import TASK_NAME_MAX_LENGTH, PriorityEnum


class Task(BaseModel):
    name: str = Field(max_length=TASK_NAME_MAX_LENGTH)
    priority: PriorityEnum
    due_date: datetime | None = None
    subtask_ids: list[int] = []
    supertask_ids: list[int] = []
    pillar_ids: list[int] = []

    @model_validator(mode="after")
    def validate_frog_has_due_date(self) -> Self:
        if self.priority is PriorityEnum.FROG and self.due_date is None:
            raise ValueError("Frog tasks must have a due date") # TODO: Should this be ValidationError?
        return self

class TaskPatch(BaseModel):
    name: str | None = Field(default=None, max_length=TASK_NAME_MAX_LENGTH)
    priority: PriorityEnum | None = None
    due_date: datetime | None = None
    subtask_ids: list[int] | None = None
    supertask_ids: list[int] | None = None
    pillar_ids: list[int] | None = None
    completed_at: datetime | None = None
    sort_key: str | None = None
