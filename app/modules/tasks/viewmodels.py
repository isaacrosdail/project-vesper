from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from datetime import datetime

    from app.modules.tasks.models import PriorityEnum, Task

from app.shared.view_mixins import BasePresenter, BaseViewModel, HasDueDateMixin


class TaskPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = ["name", "priority", "is_frog", "due_date"]
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "Task ID", "priority": "desktop-only"},
        "name": {"label": "Task", "priority": "essential"},
        "is_done": {"label": "Status", "priority": "essential"},
        "priority": {"label": "Priority", "priority": "essential"},
        "is_frog": {"label": "'Frog Task'?", "priority": "desktop-only"},
        "due_date": {"label": "Due Date", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "completed_at": {"label": "Completed", "priority": "desktop-only"},
    }


class TaskViewModel(BaseViewModel, HasDueDateMixin):
    name: str
    is_done: bool
    priority: PriorityEnum
    is_frog: bool
    due_date: datetime
    completed_at: datetime
    subtype: str

    def __init__(self, task: Task, tz: str) -> None:
        fields = {
            "id",
            "name",
            "is_done",
            "priority",
            "is_frog",
            "due_date_local",
            "completed_at",
            "subtype",
        }
        for name in fields:
            setattr(self, name, getattr(task, name))

        self.tags = task.tags
        self._tz = tz

    @property
    def priority_label(self) -> str:
        return f"{self.priority.value.title()}"

    @property
    def frog_label(self) -> str:
        return "Yes" if self.is_frog else ""

    @property
    def due_label(self) -> str:
        return self.format_due_label()
