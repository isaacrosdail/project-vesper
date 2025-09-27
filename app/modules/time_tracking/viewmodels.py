"""
Presentation layer: Wraps models to provide display-friendly fields. Think: formatting, show in local timezone, etc.
"""
from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class TimeEntryPresenter(BasePresenter):
    VISIBLE_COLUMNS = [
        "category", "duration", "started_at", "description"
    ]

    COLUMN_CONFIG = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "category": {"label": "Category", "priority": "essential"},
        "description": {"label": "Description", "priority": "essential"},
        "started_at": {"label": "Started At", "priority": "essential"},
        "duration": {"label": "Duration (mins.)", "priority": "essential"}
    }


class TimeEntryViewModel(TimestampedViewMixin):
    def __init__(self, entry, tz):
        self.id = entry.id
        self.category = entry.category
        self.duration = entry.duration_minutes
        self.description = entry.description
        self.started_at = entry.started_at
        self.ended_at = entry.ended_at
        self._tz = tz

    @property
    def duration_label(self):
        mins = int(round(self.duration))
        h, m = divmod(mins, 60)
        return f"{h}h {m:02d}m" if h else f"{m}m"

    @property
    def started_at_local(self):
        dt = self._to_local(self.started_at, self._tz)
        return dt.strftime("%I:%M%p (%d.%m.%y)")
    
    @property
    def started_label(self):
        return self.format(self.started_at, self._tz, "%I:%M %p")
    
    @property
    def desc_label(self):
        return self.description if self.description else "--"