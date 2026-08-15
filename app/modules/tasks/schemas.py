
from datetime import datetime
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator, AwareDatetime

from app.modules.tasks.models import TASK_NAME_MAX_LENGTH, PriorityEnum, Task
from app.shared.schemas import APIReadSchema, APISchema, PillarRead


class TaskRead(APIReadSchema):
    id: int
    name: str
    priority: PriorityEnum
    due_datetime: datetime | None
    sort_key: str
    completed_at: datetime | None
    created_at: datetime
    is_done: bool
    subtasks: list[int]
    supertasks: list[int]
    pillars: list[PillarRead]
    subtype: Literal['tasks']

    @field_validator("subtasks", "supertasks", mode="before")
    @classmethod
    # attr holds Task objs, but wire format is id arrays,
    #  so mode=before maps before validation
    def tasks_to_ids(cls, v: list[Task]) -> list[int]:
        return [t.id for t in v]


class TaskProgressRead(APIReadSchema):
    completed: int
    total: int
    percent: int


class TaskCreate(APISchema):
    name: str = Field(min_length=1, max_length=TASK_NAME_MAX_LENGTH)
    priority: PriorityEnum
    due_datetime: AwareDatetime | None = None
    subtask_ids: list[int] = []
    supertask_ids: list[int] = []
    pillar_ids: list[int] = []

    @model_validator(mode="after")
    def validate_frog_has_due_datetime(self) -> Self:
        if self.priority is PriorityEnum.FROG and self.due_datetime is None:
            raise ValueError("Frog tasks must have a due date")
        return self

class TaskPatch(APISchema):
    name: str | None = Field(None, min_length=1, max_length=TASK_NAME_MAX_LENGTH)
    priority: PriorityEnum | None = None
    due_datetime: AwareDatetime | None = None
    subtask_ids: list[int] | None = None
    supertask_ids: list[int] | None = None
    pillar_ids: list[int] | None = None
    completed_at: AwareDatetime | None = None
    sort_key: str | None = None

    @field_validator("name", "priority", "sort_key", "subtask_ids", "supertask_ids", "pillar_ids")
    @classmethod
    def reject_explicit_nulls(cls, v: Any | None) -> Any | None:
        if v is None:
            raise ValueError(f"Field cannot be none")
        return v


class TaskLink(APISchema):
    subtask_id: int
    supertask_id: int

    @model_validator(mode="after")
    def verify_no_self_link(self) -> Self:
        if self.subtask_id == self.supertask_id:
            raise ValueError("Self-links are invalid")
        return self

class TaskStatRead(APIReadSchema):
    rate: int
    count: int
    total: int
