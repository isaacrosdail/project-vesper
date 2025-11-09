
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.tasks.models import Task

from app.shared.view_mixins import TimestampedViewMixin, BasePresenter


class TaskPresenter(BasePresenter):
    VISIBLE_COLUMNS = [
        "name", "is_done", "priority", "due_date"
    ]
    COLUMN_CONFIG = {
        "id": {"label": "Task ID", "priority": "desktop-only"},
        "name": {"label": "Task", "priority": "essential"},
        "is_done": {"label": "Status", "priority": "essential"},
        "priority": {"label": "Priority", "priority": "essential"},
        "is_frog": {"label": "'Frog Task'?", "priority": "desktop-only"},
        "due_date": {"label": "Due Date", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "completed_at": {"label": "Completed", "priority": "desktop-only"}
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
    def due_label(self) -> str:
        return self.format_due_label()
    
    @property
    def completed_label(self) -> str:
        if not self.is_done:
            return "Not completed"
        return f"Completed {self.format_dt(self.completed_at, '%b %d, %I:%M %p')}"