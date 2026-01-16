from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from datetime import datetime

from app.shared.view_mixins import TimestampedViewMixin, BasePresenter


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

class TaskViewModel(TimestampedViewMixin):
    def __init__(self, task: 'Task', tz: str):
        self.id = task.id
        self.name = task.name
        self.is_done = task.is_done
        self.priority = task.priority
        self.is_frog = task.is_frog
        self.due_date = task.due_date
        self.completed_at = task.completed_at
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
