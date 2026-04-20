from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from app.modules.tasks.models import Task

from app.shared.view_mixins import BasePresenter, BaseViewModel, HasDueDateMixin


class TaskPresenter(BasePresenter):
    VISIBLE_COLUMNS: ClassVar[list[str]] = ["name", "due_date"]
    COLUMN_CONFIG: ClassVar[dict[str, dict[str, str]]] = {
        "id": {"label": "Task ID", "priority": "desktop-only"},
        "name": {"label": "Task", "priority": "essential"},
        "is_done": {"label": "Status", "priority": "essential"},
        "due_date": {"label": "Due Date", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "completed_at": {"label": "Completed", "priority": "desktop-only"},
    }


class TaskViewModel(BaseViewModel, HasDueDateMixin):
    __slots__ = (
        "completed_at",
        "due_date_local",
        "id",
        "is_done",
        "name",
        "priority",
        "subtype",
        "tags",
    )

    def __init__(self, task: Task, tz: str) -> None:
        self.name = task.name
        self.is_done = task.is_done
        self.priority = task.priority
        self.due_date_local = task.due_date_local
        self.completed_at = task.completed_at
        self.subtype = task.subtype
        self.tags = task.tags
        self.id = task.id
        self._tz = tz


    @property
    def due_label(self) -> str:
        return self.format_due_label()
