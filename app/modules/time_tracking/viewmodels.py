"""
Presentation layer: Wraps models to provide display-friendly fields. Think: formatting, show in local timezone, etc.
"""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.modules.time_tracking.models import TimeEntry


from app.shared.view_mixins import TimestampedViewMixin, BasePresenter

class TimeEntryPresenter(BasePresenter):
    VISIBLE_COLUMNS = [
        "date", "category", "time_window", "description"
    ]

    COLUMN_CONFIG = {
        "id": {"label": "ID", "priority": "desktop-only"},
        "category": {"label": "Category", "priority": "essential"},
        "description": {"label": "Description", "priority": "essential"},
        "time_window": {"label": "Time Window (Duration)", "priority": "essential", "sort_field": "started_at"},
        "date": {"label": "Date", "priority": "essential", "sort_field": "started_at"}
    }


class TimeEntryViewModel(TimestampedViewMixin):
    def __init__(self, entry: 'TimeEntry', tz: str):
        self.id = entry.id
        self.category = entry.category
        self.duration = entry.duration_minutes
        self.description = entry.description
        self.started_at = entry.started_at
        self.ended_at = entry.ended_at
        self._tz = tz

    @property
    def date_label(self) -> str:
        return self.format_dt(self.started_at, fmt="%m/%d")
    
    @property
    def time_window_label(self) -> str:
        mins = self.duration
        h, m = divmod(mins, 60)
        duration = f"{h}h{m:02d}m" if h else f"{m}m"
        start = self.format_dt(self.started_at, fmt="%I:%M%p")
        end = self.format_dt(self.ended_at, fmt="%I:%M%p")
        return f"{start}-{end} ({duration})"

    @property
    def started_at_label(self) -> str:
        return self.format_dt(self.started_at, fmt="%I:%M%p (%d.%m.%y)")
    
    @property
    def desc_label(self) -> str:
        return self.description if self.description else "--"