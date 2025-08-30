
from app.shared.view_mixins import TimestampedViewMixin

class HabitPresenter:
    VISIBLE_COLUMNS = [
        "name", "status", "created_at"
    ]
    # Human-readable column names
    COLUMN_LABELS = {
        "id": "ID",
        "name": "Name",
        "tags": "Tag(s)",
        "status": "Status",
        "created_at": "Created",
        "established_date": "Date Promoted",
        "promotion_threshold": "Promotion Threshold"
    }

    @classmethod
    def build_columns(cls) -> list[dict]:
        return [{"key": c, "label": cls.COLUMN_LABELS.get(c, c)} for c in cls.VISIBLE_COLUMNS]
    
class HabitViewModel(TimestampedViewMixin):
    def __init__(self, habit, tz):
        self.id = habit.id
        self.name = habit.name
        self.status = habit.status
        self.established_date = habit.established_date
        self.promotion_threshold = habit.promotion_threshold
        self.created_at = habit.created_at
        self._tz = tz
    
    @property
    def status_label(self):
        return f"{self.status.value}"
    
    @property
    def created_at_label(self):
        return self.format(self.created_at, self._tz, "%d.%m.%Y")