
from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class HabitPresenter(BasePresenter):
    VISIBLE_COLUMNS = [
        "name", "status", "created_at"
    ]
    COLUMN_CONFIG = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "name": {"label": "Name", "priority": "essential"},
        "tags": {"label": "Tag(s)", "priority": "desktop-only"},
        "status": {"label": "Status", "priority": "essential"},
        "created_at": {"label": "Created", "priority": "desktop-only"},
        "established_date": {"label": "Date Promoted", "priority": "desktop-only"},
        "promotion_threshold": {"label": "Promotion Threshold", "priority": "desktop-only"}
    }

    
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
        return f"{self.status.value.title()}"
    
    @property
    def created_at_label(self):
        return self.format_created_at_label()