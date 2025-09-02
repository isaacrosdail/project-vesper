
from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class TaskPresenter(BasePresenter):
    # View-specific table config
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
    def __init__(self, task, tz):
        self.id = task.id
        self.name = task.name
        self.is_done = task.is_done
        self.priority = task.priority   # Enum instance
        self.is_frog = task.is_frog
        self.due_date = task.due_date
        self.tags = task.tags
        self._tz = tz

    @property
    def due_date_local(self):
        return self._to_local(self.due_date, self._tz)
    
    @property
    def due_label(self):
        return self.format(self.due_date, self._tz, "%I:%M %p")
    
    @property
    def completed_label(self):
        pass