
from app.shared.view_mixins import TimestampedViewMixin

class TaskPresenter:
    # View-specific table config
    VISIBLE_COLUMNS = [
        "name", "is_done", "priority", "due_date"
    ]
    COLUMN_LABELS = {
        "id": "Task ID",
        "name": "Task",
        "is_done": "Status",
        "priority": "Priority",
        "is_frog": "'Frog Task'?",
        "due_date": "Due Date",
        "created_at": "Created",
        "completed_at": "Completed",
    }

    # TODO: NOTES: First arg is the class (cls) instead of the instance (self)
    # Used when the method works with class-level data (metadata, config, alt constructors)
    @classmethod
    def build_columns(cls) -> list[dict]:
        """
        Builds a list of column definitions for use as table headers.
        Respects the order defined in `VISIBLE_COLUMNS` & excludes fields not explicitly whitelisted.
        """
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]

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